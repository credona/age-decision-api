from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_verify_declares_error_responses():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    verify = payload["paths"]["/verify"]["post"]
    responses = verify["responses"]

    assert "400" in responses
    assert "502" in responses


def test_openapi_verify_response_contains_v2_global_score_fields():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    schema = payload["components"]["schemas"]["VerifyResponse"]
    properties = schema["properties"]

    assert "cred_global_score" in properties
    assert "cred_score" not in properties
    assert "age_check" in properties
    assert "liveness_check" in properties
