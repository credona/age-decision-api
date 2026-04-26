from typing import Any

from app.types import LivenessCheck


def _score_from_raw(antispoof_decision: dict[str, Any]) -> float:
    """
    Extract the best available anti-spoof score from the antispoof response.
    """
    score = antispoof_decision.get("cred_antispoof_score")

    if score is None:
        score = antispoof_decision.get("confidence")

    if score is None:
        return 0.0

    return max(0.0, min(float(score), 1.0))


def normalize_liveness_check(
    antispoof_decision: dict[str, Any],
) -> LivenessCheck:
    """
    Normalize age-decision-antispoof response into a unified contract.
    """
    is_real = antispoof_decision.get("is_real")
    spoof_detected = antispoof_decision.get("spoof_detected")
    decision = antispoof_decision.get("decision")

    passed = (
        decision in ["real", "allow"]
        or is_real is True
        or spoof_detected is False
    )

    return {
        "status": "passed" if passed else "failed",
        "decision": "allow" if passed else "deny",
        "reason": None if passed else antispoof_decision.get("rejection_reason") or antispoof_decision.get("reason") or "liveness_check_failed",
        "confidence": antispoof_decision.get("confidence"),
        "is_real": is_real,
        "spoof_detected": spoof_detected,
        "cred_antispoof_score": _score_from_raw(antispoof_decision),
    }