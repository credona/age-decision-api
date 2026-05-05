from fastapi.testclient import TestClient

from app.main import app
from app.application.use_cases.verification_orchestrator import (
    verification_orchestrator,
)

client = TestClient(app)


def test_verify_invalid_base64_returns_standardized_error_contract():
    response = client.post(
        "/verify",
        headers={
            "X-Request-ID": "test-request-invalid-b64",
            "X-Correlation-ID": "test-correlation-invalid-b64",
        },
        json={
            "image_base64": "invalid-base64!",
        },
    )

    assert response.status_code == 400

    payload = response.json()

    assert set(payload.keys()) == {"request_id", "correlation_id", "error"}
    assert set(payload["error"].keys()) == {"code", "message"}

    assert payload["request_id"] == "test-request-invalid-b64"
    assert payload["correlation_id"] == "test-correlation-invalid-b64"
    assert payload["error"]["code"] == "invalid_base64_image"
    assert payload["error"]["message"] == "Invalid request."


def test_verify_missing_image_base64_returns_stable_validation_error_shape():
    response = client.post(
        "/verify",
        headers={
            "X-Request-ID": "test-request-missing-payload-field",
            "X-Correlation-ID": "test-correlation-missing-payload-field",
        },
        json={
            "majority_country": "FR",
        },
    )

    assert response.status_code == 400

    payload = response.json()

    assert set(payload.keys()) == {"request_id", "correlation_id", "error"}
    assert set(payload["error"].keys()) == {"code", "message"}
    assert payload["request_id"] == "test-request-missing-payload-field"
    assert payload["correlation_id"] == "test-correlation-missing-payload-field"
    assert payload["error"]["code"] == "missing_image_base64"
    assert payload["error"]["message"] == "Invalid request."


def test_verify_missing_image_base64_falls_back_to_request_id_as_correlation_id():
    response = client.post(
        "/verify",
        headers={
            "X-Request-ID": "test-request-missing-b64-corr-fallback",
        },
        json={
            "majority_country": "FR",
        },
    )

    assert response.status_code == 400

    payload = response.json()

    assert payload["request_id"] == "test-request-missing-b64-corr-fallback"
    assert payload["correlation_id"] == "test-request-missing-b64-corr-fallback"
    assert payload["error"]["code"] == "missing_image_base64"
    assert payload["error"]["message"] == "Invalid request."


def test_verify_downstream_exception_returns_standardized_502(monkeypatch):
    async def fail_verify(*_, **__) -> dict:
        raise RuntimeError("simulated downstream failure")

    monkeypatch.setattr(verification_orchestrator, "verify_image_base64", fail_verify)

    response = client.post(
        "/verify",
        headers={
            "X-Request-ID": "test-request-502",
            "X-Correlation-ID": "test-correlation-502",
        },
        json={
            "image_base64": "Zm9v",
        },
    )

    assert response.status_code == 502

    payload = response.json()

    assert set(payload.keys()) == {"request_id", "correlation_id", "error"}
    assert set(payload["error"].keys()) == {"code", "message"}

    assert payload["request_id"] == "test-request-502"
    assert payload["correlation_id"] == "test-correlation-502"
    assert payload["error"]["code"] == "downstream_service_error"
    assert payload["error"]["message"] == "An upstream service error has occurred."
