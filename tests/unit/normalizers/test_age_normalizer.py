from app.normalizers.age_normalizer import normalize_age_check


def test_age_normalizer_pass():
    raw = {
        "decision": "adult",
        "is_adult": True,
        "estimated_age": 25,
        "confidence": 0.9,
    }

    result = normalize_age_check(raw)

    assert result["status"] == "passed"
    assert result["decision"] == "allow"
    assert result["reason"] is None


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