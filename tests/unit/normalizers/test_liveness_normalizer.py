from app.normalizers.liveness_normalizer import normalize_liveness_check


def test_liveness_normalizer_pass():
    raw = {
        "decision": "real",
        "is_real": True,
        "spoof_detected": False,
        "cred_antispoof_score": 0.91,
    }

    result = normalize_liveness_check(raw)

    assert result["status"] == "passed"
    assert result["decision"] == "allow"
    assert result["reason"] is None
    assert result["is_real"] is True
    assert result["spoof_detected"] is False
    assert result["cred_antispoof_score"] == 0.91


def test_liveness_normalizer_fail():
    raw = {
        "decision": "spoof",
        "is_real": False,
        "spoof_detected": True,
        "rejection_reason": "spoof_detected",
        "cred_antispoof_score": 0.2,
    }

    result = normalize_liveness_check(raw)

    assert result["status"] == "failed"
    assert result["decision"] == "deny"
    assert result["reason"] == "spoof_detected"
    assert result["cred_antispoof_score"] == 0.2


def test_liveness_normalizer_defaults_score_to_zero():
    raw = {
        "decision": "spoof",
        "is_real": False,
        "spoof_detected": True,
    }

    result = normalize_liveness_check(raw)

    assert result["cred_antispoof_score"] == 0.0
