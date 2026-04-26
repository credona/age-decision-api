from typing import Any

from app.types import AgeCheck


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
    Extract the best available decision score from the core response.
    """
    score = _extract_score(age_decision.get("cred_decision_score"))

    if score is None:
        score = _extract_score(age_decision.get("cred_score"))

    if score is None:
        score = _extract_score(age_decision.get("confidence"))

    return score if score is not None else 0.0


def normalize_age_check(age_decision: dict[str, Any]) -> AgeCheck:
    """
    Normalize age-decision-core response into a unified contract.
    """
    is_adult = age_decision.get("is_adult")
    decision = age_decision.get("decision")

    passed = decision in ["adult", "allow"] or is_adult is True

    return {
        "status": "passed" if passed else "failed",
        "decision": "allow" if passed else "deny",
        "reason": None
        if passed
        else age_decision.get("rejection_reason")
        or age_decision.get("reason")
        or "age_check_failed",
        "estimated_age": age_decision.get("estimated_age"),
        "confidence": age_decision.get("confidence"),
        "is_adult": is_adult,
        "cred_decision_score": _score_from_raw(age_decision),
    }