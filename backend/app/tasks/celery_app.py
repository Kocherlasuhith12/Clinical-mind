from celery import Celery
from app.config import settings

celery_app = Celery(
    "clinicalmind",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.celery_app"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="run_diagnosis_pipeline", bind=True, max_retries=3)
def run_diagnosis_pipeline(self, case_id: str, use_offline: bool = False):
    try:
        from app.diagnosis.pipeline import run_full_pipeline
        run_full_pipeline(case_id, use_offline=use_offline)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="sync_offline_cases")
def sync_offline_cases_task():
    """Periodic task to retry failed offline syncs."""
    from app.db.session import SessionLocal
    from app.db.models import SyncQueue
    from datetime import datetime

    db = SessionLocal()
    try:
        pending = db.query(SyncQueue).filter(
            SyncQueue.synced == False,
            SyncQueue.retries < 5
        ).all()
        for item in pending:
            run_diagnosis_pipeline.delay(str(item.case_id))
            item.retries += 1
        db.commit()
    finally:
        db.close()


# Periodic tasks
from celery.schedules import crontab
celery_app.conf.beat_schedule = {
    "sync-offline-every-5-min": {
        "task": "sync_offline_cases",
        "schedule": crontab(minute="*/5"),
    },
}
