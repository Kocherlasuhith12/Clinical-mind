from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

from app.db.session import get_db
from app.db.models import User, AuditLog, UserRole, Language
from app.auth.jwt import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.asha
    language: Language = Language.en
    clinic_id: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    role: str
    language: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    language: str
    clinic_id: Optional[str]

    class Config:
        from_attributes = True


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=uuid.uuid4(),
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role,
        language=req.language,
        clinic_id=uuid.UUID(req.clinic_id) if req.clinic_id else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        name=user.name,
        role=user.role,
        language=user.language,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None,
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    log = AuditLog(user_id=user.id, action="login",
                   ip_address=request.client.host if request else None)
    db.add(log)
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        name=user.name,
        role=user.role,
        language=user.language,
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        language=current_user.language,
        clinic_id=str(current_user.clinic_id) if current_user.clinic_id else None,
    )
