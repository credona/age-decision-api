from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_openapi_verify_declares_error_response_schema():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    verify_endpoint = payload["paths"]["/verify"]["post"]
    responses = verify_endpoint["responses"]

    assert "400" in responses
    assert "502" in responses
    assert responses["400"]["content"]["application/json"]["schema"]["$ref"] == (
        "#/components/schemas/ErrorResponse"
    )
    assert responses["502"]["content"]["application/json"]["schema"]["$ref"] == (
        "#/components/schemas/ErrorResponse"
    )


def test_openapi_verify_response_contains_global_score_fields():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    schema = payload["components"]["schemas"]["VerifyResponse"]
    properties = schema["properties"]

    assert "cred_global_score" in properties
    assert "cred_score" in properties