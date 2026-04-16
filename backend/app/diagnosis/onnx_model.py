"""
Offline inference using a lightweight ONNX model.
This runs locally on the device when internet is unavailable.

For production: fine-tune a small model (e.g. Phi-3-mini or Llama-3.2-1B)
on Indian medical symptom data and export to ONNX format.
Place the model file at: backend/models/clinicalmind_offline.onnx
"""
import json
import os
from typing import Optional, List

ONNX_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/clinicalmind_offline.onnx")

# Common Indian primary care conditions for offline fallback
SYMPTOM_RULES = {
    ("fever", "chills", "headache"): {
        "primary_dx": "Suspected Malaria",
        "differentials": [
            {"name": "Malaria (P. vivax)", "confidence": 0.6, "reason": "Cyclical fever pattern"},
            {"name": "Dengue fever", "confidence": 0.25, "reason": "Common in endemic areas"},
            {"name": "Typhoid", "confidence": 0.15, "reason": "Sustained fever"},
        ],
        "confidence": 0.65,
        "is_emergency": False,
        "treatment_plan": "Rapid malaria test (RDT) immediately. If positive: artemisinin-based combination therapy per NHM protocol. Paracetamol for fever. Oral rehydration.",
        "precautions": "Watch for severe headache, altered consciousness, or jaundice — refer immediately.",
        "when_to_refer": "Positive RDT with vomiting, unable to take oral medication, or severe malaria symptoms.",
    },
    ("cough", "breathing difficulty", "chest pain"): {
        "primary_dx": "Suspected Pneumonia / LRTI",
        "differentials": [
            {"name": "Community-acquired pneumonia", "confidence": 0.55, "reason": "Productive cough + chest symptoms"},
            {"name": "Tuberculosis", "confidence": 0.3, "reason": "High TB burden in India"},
            {"name": "Asthma exacerbation", "confidence": 0.15, "reason": "Wheeze possible"},
        ],
        "confidence": 0.60,
        "is_emergency": False,
        "treatment_plan": "Assess respiratory rate. Amoxicillin 500mg TDS for 5 days if bacterial. Sputum AFB if cough >2 weeks. Refer if SpO2 <94%.",
        "precautions": "Red flags: cyanosis, RR>30, inability to speak full sentences.",
        "when_to_refer": "SpO2 below 94%, high fever not responding to treatment, suspected TB.",
    },
    ("diarrhea", "vomiting", "dehydration"): {
        "primary_dx": "Acute Gastroenteritis with Dehydration",
        "differentials": [
            {"name": "Acute gastroenteritis", "confidence": 0.7, "reason": "Primary presentation"},
            {"name": "Cholera", "confidence": 0.2, "reason": "If outbreak area"},
            {"name": "Food poisoning", "confidence": 0.1, "reason": "Recent food intake"},
        ],
        "confidence": 0.75,
        "is_emergency": False,
        "treatment_plan": "ORS 200ml after every loose stool. Zinc 20mg/day for 14 days (children). Continue breastfeeding. BRAT diet.",
        "precautions": "Watch for sunken eyes, no urine output >6h, blood in stool.",
        "when_to_refer": "Unable to retain fluids, bloody diarrhea, signs of severe dehydration, IV fluids needed.",
    },
}

EMERGENCY_KEYWORDS = [
    "unconscious", "not breathing", "severe chest pain", "stroke",
    "convulsion", "seizure", "severe bleeding", "snake bite", "poisoning",
    "heart attack", "paralysis", "cannot speak"
]


def run_offline_diagnosis(
    symptoms_text: str,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
) -> dict:
    """
    Offline inference: rule-based fallback when no internet.
    In production, replace with actual ONNX model inference.
    """
    symptoms_lower = symptoms_text.lower()

    # Emergency check
    is_emergency = any(kw in symptoms_lower for kw in EMERGENCY_KEYWORDS)
    if is_emergency:
        return {
            "primary_dx": "EMERGENCY — Immediate Referral Required",
            "differentials": [],
            "confidence": 0.95,
            "is_emergency": True,
            "emergency_reason": "Life-threatening symptoms detected. Activate emergency transport immediately.",
            "treatment_plan": "Call 108 ambulance. Keep patient still and comfortable. Do not give food or water.",
            "precautions": "Monitor breathing and pulse. Begin CPR if needed.",
            "when_to_refer": "IMMEDIATELY",
            "model_used": "offline-rules",
        }

    # Match symptom patterns
    for keywords, result in SYMPTOM_RULES.items():
        matches = sum(1 for kw in keywords if kw in symptoms_lower)
        if matches >= 2:
            result["model_used"] = "offline-rules"
            return result

    # Generic fallback
    return {
        "primary_dx": "Assessment incomplete — online diagnosis recommended",
        "differentials": [],
        "confidence": 0.3,
        "is_emergency": False,
        "emergency_reason": None,
        "treatment_plan": "Record symptoms carefully. Provide supportive care. Sync for full AI diagnosis when connected.",
        "precautions": "Monitor patient. If condition worsens, refer to nearest CHC.",
        "when_to_refer": "If no improvement in 24-48 hours or symptoms worsen.",
        "model_used": "offline-rules",
    }
