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


def _decision_check(decision: str) -> dict:
    status = {
        "allow": "passed",
        "deny": "failed",
        "inconclusive": "unknown",
    }[decision]

    return {
        "status": status,
        "decision": decision,
        "reason": None if decision == "allow" else "threshold_uncertain",
        "threshold": {
            "type": "minimum_age",
            "value": 18,
            "source": "default",
            "majority_country": None,
        },
        "cred_decision_score": 0.0 if decision == "inconclusive" else 0.8,
    }


def _spoof_check(decision: str) -> dict:
    return {
        "status": "passed" if decision == "allow" else "failed",
        "decision": decision,
        "reason": None if decision == "allow" else "spoof_detected",
        "is_real": decision == "allow",
        "spoof_detected": decision == "deny",
        "cred_antispoof_score": 0.9 if decision == "allow" else 0.2,
    }


@pytest.mark.parametrize(
    ("core_decision", "spoof_decision", "expected"),
    [
        ("allow", "allow", "allow"),
        ("deny", "allow", "deny"),
        ("inconclusive", "allow", "inconclusive"),
        ("allow", "deny", "deny"),
        ("deny", "deny", "deny"),
        ("inconclusive", "deny", "deny"),
    ],
)
def test_aggregate_three_state_matrix(
    core_decision: str,
    spoof_decision: str,
    expected: str,
):
    service = VerificationOrchestrator()

    result = service.aggregate(
        decision_check=_decision_check(core_decision),
        spoof_check=_spoof_check(spoof_decision),
    )

    assert result == expected


def test_build_reason_preserves_inconclusive_reason():
    service = VerificationOrchestrator()

    decision_check = _decision_check("inconclusive")
    spoof_check = _spoof_check("allow")

    result = service.build_reason(
        decision="inconclusive",
        decision_check=decision_check,
        spoof_check=spoof_check,
    )

    assert result == "threshold_uncertain"


def test_build_reason_prioritizes_spoof_denial_over_core_inconclusive():
    service = VerificationOrchestrator()

    decision_check = _decision_check("inconclusive")
    spoof_check = _spoof_check("deny")

    result = service.build_reason(
        decision="deny",
        decision_check=decision_check,
        spoof_check=spoof_check,
    )

    assert result == "spoof_detected"
