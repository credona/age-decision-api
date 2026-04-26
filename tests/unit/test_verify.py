import base64

from fastapi.testclient import TestClient

from app.main import app
from app.services.decision_service import decision_service

client = TestClient(app)


def test_verify_without_body():
    response = client.post("/verify")

    assert response.status_code == 422


def test_verify_invalid_base64():
    response = client.post(
        "/verify",
        json={
            "image_base64": "invalid-base64",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["error"] == "invalid_base64_image"


def test_verify_success(monkeypatch):
    async def fake_verify_image_base64(
        image_base64,
        request_id=None,
        correlation_id=None,
        country=None,
        age_threshold=None,
        age_margin=None,
        confidence_threshold=None,
    ):
        return {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "decision": "allow",
            "cred_score": 0.8,
            "age_check": {
                "status": "passed",
                "decision": "allow",
                "reason": None,
                "estimated_age": 76.0,
                "confidence": 0.8,
                "is_adult": True,
                "cred_decision_score": 0.8,
            },
            "liveness_check": {
                "status": "passed",
                "decision": "allow",
                "reason": None,
                "confidence": 0.99,
                "is_real": True,
                "spoof_detected": False,
                "cred_antispoof_score": 0.99,
            },
            "privacy": {
                "image_stored": False,
                "biometric_template_stored": False,
                "raw_image_logged": False,
                "downstream_raw_response_exposed": False,
                "retention_policy": "not_stored_by_api_gateway",
            },
            "zk_proof": {
                "zk_ready": True,
                "proof_type": "interactive_zero_knowledge_ready",
                "proof_status": "not_generated",
                "statement": "The API is ready to prove an age decision without exposing the raw image or estimated age.",
            },
            "reason": None,
        }

    monkeypatch.setattr(
        decision_service,
        "verify_image_base64",
        fake_verify_image_base64,
    )

    image_base64 = base64.b64encode(b"fake-image").decode("utf-8")

    response = client.post(
        "/verify",
        headers={
            "X-Request-ID": "test-request-001",
            "X-Correlation-ID": "test-correlation-001",
        },
        json={
            "image_base64": image_base64,
            "country": "FR",
            "age_threshold": 18,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["request_id"] == "test-request-001"
    assert data["correlation_id"] == "test-correlation-001"
    assert data["decision"] == "allow"
    assert data["cred_score"] == 0.8
    assert data["age_check"]["cred_decision_score"] == 0.8
    assert data["liveness_check"]["cred_antispoof_score"] == 0.99
    assert data["privacy"]["image_stored"] is False
    assert data["zk_proof"]["zk_ready"] is True
    assert "raw" not in data