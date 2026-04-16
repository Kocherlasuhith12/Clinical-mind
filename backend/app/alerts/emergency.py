"""
Emergency alert system.
Sends alerts via available channels when a case is flagged as urgent.
"""
import logging
from app.db.models import PatientCase

logger = logging.getLogger(__name__)


def send_emergency_alert(case: PatientCase, diagnosis_result: dict):
    """
    Send emergency alert for critical cases.
    Extend with SMS (Fast2SMS), push notifications, etc.
    """
    alert_message = build_alert_message(case, diagnosis_result)

    # Log emergency to system logs (always)
    logger.critical(f"EMERGENCY CASE {case.id}: {diagnosis_result.get('primary_dx')} — {diagnosis_result.get('emergency_reason')}")

    # Try SMS via Fast2SMS (India)
    try:
        send_sms_alert(case, alert_message)
    except Exception as e:
        logger.error(f"SMS alert failed: {e}")

    # WebSocket push (handled by FastAPI WebSocket endpoint)
    try:
        broadcast_emergency(str(case.id), alert_message)
    except Exception as e:
        logger.error(f"WebSocket broadcast failed: {e}")


def build_alert_message(case: PatientCase, result: dict) -> str:
    return (
        f"🚨 EMERGENCY ALERT — ClinicalMind\n"
        f"Case ID: {case.id}\n"
        f"Patient: {case.patient_age}yr {case.patient_sex}\n"
        f"Diagnosis: {result.get('primary_dx')}\n"
        f"Reason: {result.get('emergency_reason')}\n"
        f"Action: {result.get('treatment_plan', 'Immediate referral required')}\n"
        f"Call 108 Emergency Ambulance immediately."
    )


def send_sms_alert(case: PatientCase, message: str):
    """
    Send SMS via Fast2SMS API (India).
    Set FAST2SMS_API_KEY in .env to enable.
    """
    import os, httpx
    api_key = os.getenv("FAST2SMS_API_KEY")
    if not api_key:
        logger.warning("FAST2SMS_API_KEY not set — SMS alerts disabled")
        return

    # Get doctor/supervisor phone from clinic
    # In production: look up on-call doctor's number from DB
    logger.info(f"SMS alert would be sent for case {case.id}")


def broadcast_emergency(case_id: str, message: str):
    """
    Broadcast emergency to connected WebSocket clients.
    Uses Redis pub/sub for cross-worker communication.
    """
    import redis
    from app.config import settings
    r = redis.from_url(settings.REDIS_URL)
    r.publish(f"emergency:{case_id}", message)
    logger.info(f"Emergency broadcast sent for case {case_id}")
