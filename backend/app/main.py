from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import redis.asyncio as aioredis
import asyncio, json, logging, os

from app.config import settings
from app.auth.router import router as auth_router
from app.cases.router import router as cases_router
from app.db.session import engine
from app.db import models
from app.cases.pdf_report import generate_case_pdf

logger = logging.getLogger(__name__)

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ClinicalMind API",
    description="AI Diagnostic Support for Rural Healthcare — India",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cases_router)

# Serve uploaded files (images, audio) locally
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def root():
    return {
        "service": "ClinicalMind API",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ── WebSocket: real-time diagnosis status ──────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, case_id: str, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(case_id, []).append(ws)

    def disconnect(self, case_id: str, ws: WebSocket):
        if case_id in self.active:
            self.active[case_id].remove(ws)

    async def broadcast(self, case_id: str, message: dict):
        for ws in self.active.get(case_id, []):
            try:
                await ws.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@app.websocket("/ws/cases/{case_id}/status")
async def case_status_ws(case_id: str, websocket: WebSocket):
    await manager.connect(case_id, websocket)
    try:
        # Subscribe to Redis channel for this case
        r = aioredis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()
        await pubsub.subscribe(f"case_status:{case_id}", f"emergency:{case_id}")

        async def listen():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode()
                    await manager.broadcast(case_id, {"type": "update", "data": data})

        listen_task = asyncio.create_task(listen())

        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
            except WebSocketDisconnect:
                break

        listen_task.cancel()
        await pubsub.unsubscribe()
        await r.close()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(case_id, websocket)


# ── PDF export endpoint ────────────────────────────────────────────────────
@app.get("/cases/{case_id}/export")
def export_case_pdf(case_id: str):
    from app.db.session import SessionLocal
    from app.db.models import PatientCase

    db = SessionLocal()
    try:
        case = db.query(PatientCase).filter(PatientCase.id == case_id).first()
        if not case:
            from fastapi import HTTPException
            raise HTTPException(404, "Case not found")

        case_dict = {
            "id": str(case.id),
            "patient_age": case.patient_age,
            "patient_sex": case.patient_sex,
            "symptoms_text": case.symptoms_text,
            "created_at": case.created_at.isoformat(),
            "status": case.status,
        }
        diag_dict = {}
        if case.diagnosis:
            d = case.diagnosis
            diag_dict = {
                "primary_dx": d.primary_dx,
                "differentials": d.differentials or [],
                "confidence": float(d.confidence) if d.confidence else 0,
                "is_emergency": d.is_emergency,
                "emergency_reason": d.emergency_reason,
                "treatment_plan": d.treatment_plan,
                "precautions": d.precautions,
                "when_to_refer": d.when_to_refer,
                "references": d.references or [],
            }

        pdf_bytes = generate_case_pdf(case_dict, diag_dict)
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=case-{case_id[:8]}.pdf"},
        )
    finally:
        db.close()
