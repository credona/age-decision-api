import base64

import pytest

from app.application.use_cases.verification_orchestrator import VerificationOrchestrator


@pytest.mark.asyncio
async def test_decode_base64_image():
    service = VerificationOrchestrator()

    payload = base64.b64encode(b"fake-image").decode("utf-8")

    result = service.decode_base64_image(payload)

    assert result == b"fake-image"


@pytest.mark.asyncio
async def test_decode_data_url_base64_image():
    service = VerificationOrchestrator()

    encoded = base64.b64encode(b"fake-image").decode("utf-8")
    payload = f"data:image/jpeg;base64,{encoded}"

    result = service.decode_base64_image(payload)

    assert result == b"fake-image"


def test_decode_invalid_base64_image():
    service = VerificationOrchestrator()

    with pytest.raises(ValueError, match="invalid_base64_image"):
        service.decode_base64_image("invalid-base64")


def test_compute_cred_global_score_uses_lowest_score():
    service = VerificationOrchestrator()

    result = service.compute_cred_global_score(
        decision_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
            "cred_decision_score": 0.82,
        },
        spoof_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
            "cred_antispoof_score": 0.97,
        },
    )

    assert result == 0.82


def test_compute_cred_global_score_keeps_lowest_score_when_inputs_are_valid():
    service = VerificationOrchestrator()

    result = service.compute_cred_global_score(
        decision_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
            "threshold": {
                "type": "minimum_age",
                "value": 18,
                "source": "default",
                "majority_country": None,
            },
            "cred_decision_score": 0.82,
        },
        spoof_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
            "is_real": True,
            "spoof_detected": False,
            "cred_antispoof_score": 0.97,
        },
    )

    assert result == 0.82


def test_aggregate_allow_when_all_checks_allow():
    service = VerificationOrchestrator()

    result = service.aggregate(
        decision_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
        },
        spoof_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
        },
    )

    assert result == "allow"


def test_aggregate_deny_when_decision_check_fails():
    service = VerificationOrchestrator()

    result = service.aggregate(
        decision_check={
            "status": "failed",
            "decision": "deny",
            "reason": "decision_check_failed",
        },
        spoof_check={
            "status": "passed",
            "decision": "allow",
            "reason": None,
        },
    )

    assert result == "deny"
