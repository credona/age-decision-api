from typing import Any

from app.types import AgeCheck


def _score_from_raw(age_decision: dict[str, Any]) -> float:
    """
    Extract the best available decision score from the core response.
    """
    score = age_decision.get("cred_decision_score")

    if score is None:
        score = age_decision.get("confidence")

    if score is None:
        return 0.0

    return max(0.0, min(float(score), 1.0))


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
        "reason": None if passed else age_decision.get("rejection_reason") or age_decision.get("reason") or "age_check_failed",
        "estimated_age": age_decision.get("estimated_age"),
        "confidence": age_decision.get("confidence"),
        "is_adult": is_adult,
        "cred_decision_score": _score_from_raw(age_decision),
    }