from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from pathlib import Path
import uuid, shutil, io
from datetime import datetime

from app.db.session import get_db
from app.db.models import PatientCase, Diagnosis, AuditLog, CaseStatus, Language
from app.auth.jwt import get_current_user
from app.db.models import User
from app.config import settings
from app.tasks.celery_app import run_diagnosis_pipeline

router = APIRouter(prefix="/cases", tags=["cases"])

# Local file storage — no cloud storage needed for dev
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def upload_to_r2(file: UploadFile, folder: str) -> str:
    """Save file locally. Swap this for R2 in production."""
    dest = UPLOAD_DIR / folder
    dest.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4()}-{file.filename}"
    file_path = dest / safe_name
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return f"/uploads/{folder}/{safe_name}"


class CaseSummary(BaseModel):
    id: str
    patient_age: Optional[int]
    patient_sex: Optional[str]
    status: str
    symptoms_text: Optional[str]
    created_at: str
    has_diagnosis: bool

    class Config:
        from_attributes = True


class DiagnosisOut(BaseModel):
    primary_dx: Optional[str]
    differentials: Optional[list]
    confidence: Optional[float]
    is_emergency: bool
    emergency_reason: Optional[str]
    treatment_plan: Optional[str]
    precautions: Optional[str]
    when_to_refer: Optional[str]
    references: Optional[list]
    model_used: Optional[str]
    created_at: Optional[str]


class CaseDetail(BaseModel):
    id: str
    patient_age: Optional[int]
    patient_sex: Optional[str]
    symptoms_text: Optional[str]
    symptoms_language: Optional[str]
    audio_url: Optional[str]
    image_urls: Optional[list]
    status: str
    is_offline: bool
    created_at: str
    diagnosis: Optional[DiagnosisOut]


@router.post("/submit", status_code=202)
async def submit_case(
    patient_age: int = Form(...),
    patient_sex: str = Form(...),
    symptoms_text: str = Form(""),
    symptoms_language: str = Form("en"),
    is_offline: bool = Form(False),
    audio: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    case = PatientCase(
        id=uuid.uuid4(),
        submitted_by=current_user.id,
        patient_age=patient_age,
        patient_sex=patient_sex,
        symptoms_text=symptoms_text,
        symptoms_language=symptoms_language,
        is_offline=is_offline,
        status=CaseStatus.pending,
    )

    if audio:
        case.audio_url = upload_to_r2(audio, "audio")

    image_urls = []
    if images:
        for img in images:
            url = upload_to_r2(img, "images")
            image_urls.append(url)
    case.image_urls = image_urls

    db.add(case)
    db.commit()
    db.refresh(case)

    log = AuditLog(
        user_id=current_user.id,
        case_id=case.id,
        action="submit",
        ip_address=request.client.host if request else None,
    )
    db.add(log)
    db.commit()

    # Queue async diagnosis pipeline
    run_diagnosis_pipeline.delay(str(case.id))

    return {"case_id": str(case.id), "status": "processing"}


@router.get("/", response_model=List[CaseSummary])
def list_cases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
):
    cases = (
        db.query(PatientCase)
        .filter(PatientCase.submitted_by == current_user.id)
        .order_by(PatientCase.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        CaseSummary(
            id=str(c.id),
            patient_age=c.patient_age,
            patient_sex=c.patient_sex,
            status=c.status,
            symptoms_text=c.symptoms_text[:100] if c.symptoms_text else None,
            created_at=c.created_at.isoformat(),
            has_diagnosis=c.diagnosis is not None,
        )
        for c in cases
    ]


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    case = db.query(PatientCase).filter(PatientCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if str(case.submitted_by) != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    log = AuditLog(user_id=current_user.id, case_id=case.id, action="view",
                   ip_address=request.client.host if request else None)
    db.add(log)
    db.commit()

    diag = None
    if case.diagnosis:
        d = case.diagnosis
        diag = DiagnosisOut(
            primary_dx=d.primary_dx,
            differentials=d.differentials,
            confidence=float(d.confidence) if d.confidence else None,
            is_emergency=d.is_emergency,
            emergency_reason=d.emergency_reason,
            treatment_plan=d.treatment_plan,
            precautions=d.precautions,
            when_to_refer=d.when_to_refer,
            references=d.references,
            model_used=d.model_used,
            created_at=d.created_at.isoformat() if d.created_at else None,
        )

    return CaseDetail(
        id=str(case.id),
        patient_age=case.patient_age,
        patient_sex=case.patient_sex,
        symptoms_text=case.symptoms_text,
        symptoms_language=case.symptoms_language,
        audio_url=case.audio_url,
        image_urls=case.image_urls or [],
        status=case.status,
        is_offline=case.is_offline,
        created_at=case.created_at.isoformat(),
        diagnosis=diag,
    )


@router.post("/sync")
def sync_offline_cases(
    cases: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    synced = []
    for payload in cases:
        case = PatientCase(
            id=uuid.uuid4(),
            submitted_by=current_user.id,
            patient_age=payload.get("patient_age"),
            patient_sex=payload.get("patient_sex"),
            symptoms_text=payload.get("symptoms_text"),
            symptoms_language=payload.get("symptoms_language", "en"),
            is_offline=True,
            status=CaseStatus.pending,
        )
        db.add(case)
        db.flush()
        run_diagnosis_pipeline.delay(str(case.id))
        synced.append(str(case.id))

    db.commit()
    return {"synced": len(synced), "case_ids": synced}
