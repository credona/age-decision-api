from app.domain.constants import (
    SPOOF_DECISION_REAL,
    DECISION_ALLOW,
    DECISION_DENY,
    STATUS_FAILED,
    STATUS_PASSED,
)

from typing import Any

from app.domain.types import SpoofCheck


def _extract_score(value: Any) -> float | None:
    """
    Extract a normalized score from either a raw float or a score object.
    """
    if value is None:
        return None

    if isinstance(value, dict):
        value = value.get("score")

    if value is None:
        return None

    return max(0.0, min(float(value), 1.0))


def _score_from_raw(antispoof_decision: dict[str, Any]) -> float:
    """
    Extract the public AntiSpoof decision score.
    """
    score = _extract_score(antispoof_decision.get("cred_antispoof_score"))

    return score if score is not None else 0.0


def normalize_spoof_check(
    antispoof_decision: dict[str, Any],
) -> SpoofCheck:
    """
    Normalize age-decision-antispoof v2 response into the API contract.

    AntiSpoof decisions:
    - real -> allow
    - spoof -> deny
    """
    is_real = antispoof_decision.get("is_real")
    spoof_detected = antispoof_decision.get("spoof_detected")
    decision = antispoof_decision.get("decision")

    passed = (
        decision == SPOOF_DECISION_REAL or is_real is True or spoof_detected is False
    )

    return {
        "status": STATUS_PASSED if passed else STATUS_FAILED,
        "decision": DECISION_ALLOW if passed else DECISION_DENY,
        "reason": None
        if passed
        else antispoof_decision.get("rejection_reason")
        or antispoof_decision.get("reason")
        or "spoof_check_failed",
        "is_real": is_real,
        "spoof_detected": spoof_detected,
        "cred_antispoof_score": _score_from_raw(antispoof_decision),
    }
