from app.domain.constants import (
    CORE_DECISION_MATCH,
    CORE_DECISION_UNCERTAIN,
    DECISION_ALLOW,
    DECISION_DENY,
    DECISION_INCONCLUSIVE,
    STATUS_FAILED,
    STATUS_PASSED,
    STATUS_UNKNOWN,
    THRESHOLD_SOURCE_DEFAULT,
    THRESHOLD_TYPE_MINIMUM_AGE,
)

from typing import Any

from app.domain.types import DecisionCheck


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


def _score_from_raw(age_decision: dict[str, Any]) -> float:
    """
    Extract the public Core decision score.
    """
    score = _extract_score(age_decision.get("cred_decision_score"))

    return score if score is not None else 0.0


def _threshold_from_raw(age_decision: dict[str, Any]) -> dict[str, Any]:
    """
    Extract threshold policy from Core v2 response.
    """
    threshold = age_decision.get("threshold")

    if isinstance(threshold, dict):
        return threshold

    return {
        "type": THRESHOLD_TYPE_MINIMUM_AGE,
        "value": 18,
        "source": THRESHOLD_SOURCE_DEFAULT,
        "majority_country": None,
    }


def normalize_decision_check(age_decision: dict[str, Any]) -> DecisionCheck:
    """
    Normalize age-decision-core v2 response into the public API contract.

    Core decisions:
    - match -> allow
    - uncertain -> inconclusive
    - no_match or unknown values -> deny (fail closed)
    """
    core_decision = age_decision.get("decision")
    reason = (
        age_decision.get("rejection_reason")
        or age_decision.get("reason")
        or "decision_check_failed"
    )

    if core_decision == CORE_DECISION_MATCH:
        status = STATUS_PASSED
        decision = DECISION_ALLOW
        reason = None
    elif core_decision == CORE_DECISION_UNCERTAIN:
        status = STATUS_UNKNOWN
        decision = DECISION_INCONCLUSIVE
    else:
        status = STATUS_FAILED
        decision = DECISION_DENY

    return {
        "status": status,
        "decision": decision,
        "reason": reason,
        "threshold": _threshold_from_raw(age_decision),
        "cred_decision_score": _score_from_raw(age_decision),
    }
