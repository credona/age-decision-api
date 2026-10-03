from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_calibration_summary_contract_when_no_runtime_state():
    response = client.get("/calibration/summary")

    assert response.status_code == 200

    assert response.json() == {
        "active": False,
        "summary": None,
    }


def test_calibration_summary_response_filter_strips_internal_fields(monkeypatch):
    from app.api import routes

    monkeypatch.setattr(
        routes,
        "get_api_runtime_calibration_summary",
        lambda: {
            "service": "api",
            "contract_version": "2.6",
            "model_identifier": "credona.api.fusion.v1",
            "policy_id": "api-policy-v1",
            "policy_version": "1.0.0",
            "benchmark_attestation_id": "benchmark-attestation-api",
            "activated_at": "2026-06-04T00:00:00Z",
            "private_payload": {"calibration_parameters": {"offset": 0.1}},
            "payload_hash": "sha256:private",
            "signature": "private-signature",
            "calibration_parameters": {"private": True},
        },
    )

    response = client.get("/calibration/summary")

    assert response.status_code == 200

    payload = response.json()

    assert payload == {
        "active": True,
        "summary": {
            "service": "api",
            "contract_version": "2.6",
            "model_identifier": "credona.api.fusion.v1",
            "policy_id": "api-policy-v1",
            "policy_version": "1.0.0",
            "benchmark_attestation_id": "benchmark-attestation-api",
            "activated_at": "2026-06-04T00:00:00Z",
        },
    }

    text = str(payload)
    assert "private_payload" not in text
    assert "payload_hash" not in text
    assert "signature" not in text
    assert "calibration_parameters" not in text
