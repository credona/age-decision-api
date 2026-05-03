from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_reject_image_sequence():
    response = client.post(
        "/verify",
        json={
            "input_type": "image_sequence",
            "image_base64": "fake-image",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["code"] == "UNSUPPORTED_INPUT_TYPE"
    assert "image_sequence" in body["error"]["message"]

    _assert_no_sensitive_fields(body)


def test_reject_video():
    response = client.post(
        "/verify",
        json={
            "input_type": "video",
            "image_base64": "fake-video",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["code"] == "UNSUPPORTED_INPUT_TYPE"
    assert "video" in body["error"]["message"]

    _assert_no_sensitive_fields(body)


def _assert_no_sensitive_fields(body: dict):
    text = str(body).lower()

    forbidden = [
        "estimated_age",
        "confidence",
        "threshold",
        "raw",
        "score",
        "downstream",
        "cred_decision_score",
        "cred_antispoof_score",
        "cred_global_score",
    ]

    for field in forbidden:
        assert field not in text
