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
    assert "decision_check" in properties
    assert "spoof_check" in properties


def test_openapi_error_response_schema_exposes_only_standardized_fields():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    schema = payload["components"]["schemas"]["ErrorResponse"]
    properties = schema["properties"]

    assert set(properties.keys()) == {"request_id", "correlation_id", "error"}


def test_openapi_error_detail_schema_exposes_only_standardized_fields():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    schema = payload["components"]["schemas"]["ErrorDetail"]
    properties = schema["properties"]

    assert set(properties.keys()) == {"code", "message"}


def test_openapi_public_decision_contract_is_three_state():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    payload = response.json()

    verify_decision = payload["components"]["schemas"]["VerifyResponse"]["properties"][
        "decision"
    ]
    decision_check_decision = payload["components"]["schemas"]["DecisionCheckResponse"][
        "properties"
    ]["decision"]
    spoof_check_decision = payload["components"]["schemas"]["SpoofCheckResponse"][
        "properties"
    ]["decision"]

    ternary_decisions = {"allow", "deny", "inconclusive"}
    binary_decisions = {"allow", "deny"}

    assert set(verify_decision["enum"]) == ternary_decisions
    assert set(decision_check_decision["enum"]) == ternary_decisions
    assert set(spoof_check_decision["enum"]) == binary_decisions
