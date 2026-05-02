from app.domain.normalizers.age_normalizer import normalize_age_check


def test_age_normalizer_pass():
    raw = {
        "decision": "match",
        "threshold": {
            "type": "minimum_age",
            "value": 18,
            "source": "majority_country",
            "majority_country": "FR",
        },
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
    assert result["threshold"]["value"] == 18


def test_age_normalizer_fail_for_no_match():
    raw = {
        "decision": "no_match",
        "rejection_reason": "age_check_failed",
        "threshold": {
            "type": "minimum_age",
            "value": 18,
            "source": "majority_country",
            "majority_country": "FR",
        },
        "cred_decision_score": {
            "score": 0.42,
            "level": "low",
        },
    }

    result = normalize_age_check(raw)

    assert result["status"] == "failed"
    assert result["decision"] == "deny"
    assert result["reason"] == "age_check_failed"
    assert result["cred_decision_score"] == 0.42


def test_age_normalizer_fail_for_uncertain():
    raw = {
        "decision": "uncertain",
        "rejection_reason": "threshold_uncertain",
        "threshold": {
            "type": "minimum_age",
            "value": 18,
            "source": "default",
            "majority_country": None,
        },
        "cred_decision_score": {
            "score": 0.0,
            "level": "none",
        },
    }

    result = normalize_age_check(raw)

    assert result["status"] == "failed"
    assert result["decision"] == "deny"
    assert result["reason"] == "threshold_uncertain"
    assert result["cred_decision_score"] == 0.0
