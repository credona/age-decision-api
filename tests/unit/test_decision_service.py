import base64

import pytest

from app.services.decision_service import DecisionService


@pytest.mark.asyncio
async def test_decode_base64_image():
    service = DecisionService()

    payload = base64.b64encode(b"fake-image").decode("utf-8")

    result = service.decode_base64_image(payload)

    assert result == b"fake-image"


@pytest.mark.asyncio
async def test_decode_data_url_base64_image():
    service = DecisionService()

    encoded = base64.b64encode(b"fake-image").decode("utf-8")
    payload = f"data:image/jpeg;base64,{encoded}"

    result = service.decode_base64_image(payload)

    assert result == b"fake-image"


def test_decode_invalid_base64_image():
    service = DecisionService()

    with pytest.raises(ValueError, match="invalid_base64_image"):
        service.decode_base64_image("invalid-base64")


def test_compute_cred_global_score_uses_lowest_score():
    service = DecisionService()

    result = service.compute_cred_global_score(
        age_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
            "cred_decision_score": 0.82,
        },
        liveness_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
            "cred_antispoof_score": 0.97,
        },
    )

    assert result == 0.82


def test_compute_cred_score_alias_uses_lowest_score():
    service = DecisionService()

    result = service.compute_cred_score(
        age_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
            "cred_decision_score": 0.82,
        },
        liveness_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
            "cred_antispoof_score": 0.97,
        },
    )

    assert result == 0.82


def test_aggregate_allow_when_all_checks_allow():
    service = DecisionService()

    result = service.aggregate(
        age_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
        },
        liveness_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
        },
    )

    assert result == "allow"


def test_aggregate_deny_when_age_check_fails():
    service = DecisionService()

    result = service.aggregate(
        age_check={
            "status": "failed",
            "decision": "deny",
            "reason": "age_check_failed",
        },
        liveness_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
        },
    )

    assert result == "deny"