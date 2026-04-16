"""
Main diagnosis pipeline:
1. Transcribe audio (if present)
2. Translate symptoms to English
3. Retrieve RAG context from Pinecone
4. Run GPT-4o Vision diagnosis
5. Save results to DB
6. Trigger emergency alert if needed
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import PatientCase, Diagnosis, CaseStatus
from app.diagnosis.whisper import transcribe_audio, translate_to_english
from app.diagnosis.vision import run_vision_diagnosis
from app.diagnosis.onnx_model import run_offline_diagnosis
from app.rag.retriever import retrieve_medical_context, build_rag_enhanced_prompt
from app.alerts.emergency import send_emergency_alert
from app.config import settings
import uuid, logging

logger = logging.getLogger(__name__)


def run_full_pipeline(case_id: str, use_offline: bool = False):
    """
    Full diagnosis pipeline for a case.
    Called by Celery worker.
    """
    db: Session = SessionLocal()
    try:
        case = db.query(PatientCase).filter(PatientCase.id == case_id).first()
        if not case:
            logger.error(f"Case {case_id} not found")
            return

        # Update status
        case.status = CaseStatus.processing
        db.commit()

        symptoms_text = case.symptoms_text or ""

        # Step 1: Transcribe audio if present
        if case.audio_url:
            try:
                transcript = transcribe_audio(case.audio_url, case.symptoms_language or "en")
                symptoms_text = transcript["text"]
                case.symptoms_text = symptoms_text
                db.commit()
            except Exception as e:
                logger.warning(f"Audio transcription failed: {e}")

        # Step 2: Translate to English
        try:
            symptoms_en = translate_to_english(symptoms_text, case.symptoms_language or "en")
            case.symptoms_translated = symptoms_en
            db.commit()
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            symptoms_en = symptoms_text

        # Step 3: RAG context retrieval
        rag_docs = []
        try:
            rag_docs = retrieve_medical_context(symptoms_en, top_k=5)
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")

        enhanced_symptoms = build_rag_enhanced_prompt(symptoms_en, rag_docs)

        # Step 4: Run diagnosis
        if use_offline or not settings.OPENAI_API_KEY:
            result = run_offline_diagnosis(symptoms_en, case.patient_age, case.patient_sex)
        else:
            result = run_vision_diagnosis(
                symptoms_text=enhanced_symptoms,
                image_urls=case.image_urls or [],
                patient_age=case.patient_age,
                patient_sex=case.patient_sex,
            )

        # Step 5: Save diagnosis
        diagnosis = Diagnosis(
            id=uuid.uuid4(),
            case_id=case.id,
            model_used=result.get("model_used", "gpt-4o"),
            primary_dx=result.get("primary_dx"),
            differentials=result.get("differentials", []),
            confidence=result.get("confidence"),
            is_emergency=result.get("is_emergency", False),
            emergency_reason=result.get("emergency_reason"),
            treatment_plan=result.get("treatment_plan"),
            precautions=result.get("precautions"),
            when_to_refer=result.get("when_to_refer"),
            references=[{"source": d["source"], "score": d.get("score")} for d in rag_docs],
            raw_response=result,
        )
        db.add(diagnosis)

        case.status = CaseStatus.urgent if result.get("is_emergency") else CaseStatus.done
        db.commit()

        # Step 6: Emergency alert
        if result.get("is_emergency"):
            try:
                send_emergency_alert(case, result)
            except Exception as e:
                logger.error(f"Emergency alert failed: {e}")

        logger.info(f"Pipeline completed for case {case_id}")

    except Exception as e:
        logger.error(f"Pipeline failed for case {case_id}: {e}")
        if case:
            case.status = CaseStatus.pending
            db.commit()
    finally:
        db.close()
