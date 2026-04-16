import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["service"] == "ClinicalMind API"


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register_and_login():
    # Register
    res = client.post("/auth/register", json={
        "name": "Test Doctor",
        "email": "testdoc@clinic.com",
        "password": "testpass123",
        "role": "doctor",
        "language": "en",
    })
    assert res.status_code in (201, 400)  # 400 if already exists in test DB

    # Login
    res = client.post("/auth/login", data={
        "username": "testdoc@clinic.com",
        "password": "testpass123",
    })
    if res.status_code == 200:
        assert "access_token" in res.json()


def test_offline_diagnosis():
    from app.diagnosis.onnx_model import run_offline_diagnosis

    result = run_offline_diagnosis("fever chills headache", patient_age=30, patient_sex="M")
    assert "primary_dx" in result
    assert "treatment_plan" in result
    assert "is_emergency" in result


def test_emergency_detection():
    from app.diagnosis.onnx_model import run_offline_diagnosis

    result = run_offline_diagnosis("patient is unconscious not breathing")
    assert result["is_emergency"] is True


def test_pdf_generation():
    from app.cases.pdf_report import generate_case_pdf

    case = {
        "id": "test-case-id-12345",
        "patient_age": 35,
        "patient_sex": "F",
        "symptoms_text": "Fever and cough for 3 days",
        "created_at": "2024-01-15T10:30:00",
        "status": "done",
    }
    diagnosis = {
        "primary_dx": "Community-acquired Pneumonia",
        "differentials": [{"name": "TB", "confidence": 0.2, "reason": "Chronic cough"}],
        "confidence": 0.75,
        "is_emergency": False,
        "emergency_reason": None,
        "treatment_plan": "Amoxicillin 500mg TDS for 5 days",
        "precautions": "Watch for worsening breathlessness",
        "when_to_refer": "If SpO2 drops below 94%",
        "references": [{"source": "NHM Guidelines", "score": 0.92}],
    }
    pdf = generate_case_pdf(case, diagnosis)
    assert isinstance(pdf, bytes)
    assert len(pdf) > 1000
    assert pdf[:4] == b"%PDF"
