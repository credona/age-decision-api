from app.normalizers.age_normalizer import normalize_age_check


def test_age_normalizer_pass():
    raw = {
        "decision": "adult",
        "is_adult": True,
        "estimated_age": 25,
        "confidence": 0.9,
        "cred_decision_score": {
            "score": 0.88,
            "level": "high",
        },
    }

    result = normalize_age_check(raw)

    assert result["status"] == "passed"
    assert result["decision"] == "allow"
    assert result["reason"] is None
    assert result["cred_decision_score"] == 0.88


def test_age_normalizer_uses_legacy_cred_score_fallback():
    raw = {
        "decision": "adult",
        "is_adult": True,
        "estimated_age": 25,
        "confidence": 0.9,
        "cred_score": {
            "score": 0.77,
            "level": "medium",
        },
    }

    result = normalize_age_check(raw)

    assert result["cred_decision_score"] == 0.77


def test_age_normalizer_fail():
    raw = {
        "decision": "minor",
        "is_adult": False,
        "rejection_reason": "too_young",
    }

    result = normalize_age_check(raw)

    assert result["status"] == "failed"
    assert result["decision"] == "deny"
    assert result["reason"] == "too_young"