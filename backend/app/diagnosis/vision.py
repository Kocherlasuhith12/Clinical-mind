import openai
import json
from typing import Optional, List
from app.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are ClinicalMind, an AI diagnostic support assistant for rural healthcare workers in India.

You assist trained ASHA workers and doctors — you NEVER replace a doctor. Your role is to provide clinical reasoning support.

Given patient information, you will:
1. Suggest the most likely primary diagnosis
2. List 2-4 differential diagnoses with confidence levels
3. Assess overall diagnostic confidence (0.0 to 1.0)
4. Flag if this is a medical emergency requiring immediate referral
5. Provide a practical treatment plan aligned with NHM guidelines
6. List precautions and red flag symptoms to watch for
7. Specify when to refer to a higher facility

Respond ONLY with valid JSON in this exact format:
{
  "primary_dx": "diagnosis name",
  "differentials": [
    {"name": "condition", "confidence": 0.7, "reason": "brief reason"},
    {"name": "condition", "confidence": 0.3, "reason": "brief reason"}
  ],
  "confidence": 0.85,
  "is_emergency": false,
  "emergency_reason": null,
  "treatment_plan": "step-by-step treatment",
  "precautions": "what to watch for",
  "when_to_refer": "specific conditions requiring referral",
  "clinical_notes": "additional observations"
}

Base your reasoning on:
- Indian epidemiology and endemic diseases
- National Health Mission (NHM) treatment protocols
- Resource constraints of primary health centres
- Climate and regional disease patterns in India
"""


def run_vision_diagnosis(
    symptoms_text: str,
    image_urls: Optional[List[str]] = None,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
) -> dict:
    """
    Run GPT-4o multimodal diagnosis on symptoms + optional images.
    Returns structured diagnosis dict.
    """
    user_content = []

    # Build text prompt
    patient_info = f"Patient: {patient_age or 'unknown'} year old {patient_sex or 'unknown'}\n"
    symptom_block = f"Symptoms: {symptoms_text}\n"
    user_content.append({"type": "text", "text": patient_info + symptom_block})

    # Add images if provided
    if image_urls:
        for url in image_urls[:3]:  # Max 3 images
            user_content.append({
                "type": "image_url",
                "image_url": {"url": url, "detail": "high"},
            })
        user_content.append({
            "type": "text",
            "text": "Please analyze the above clinical images along with the symptoms.",
        })

    user_content.append({
        "type": "text",
        "text": "Provide your clinical assessment as a JSON object.",
    })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=1500,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)
    result["model_used"] = "gpt-4o"
    result["raw_response"] = raw
    return result
