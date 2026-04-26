from app.normalizers.liveness_normalizer import normalize_liveness_check


def test_liveness_normalizer_pass():
    raw = {
        "decision": "real",
        "is_real": True,
        "confidence": 0.99,
        "cred_antispoof_score": 0.91,
    }

    result = normalize_liveness_check(raw)

    assert result["status"] == "passed"
    assert result["decision"] == "allow"
    assert result["reason"] is None
    assert result["cred_antispoof_score"] == 0.91


def test_liveness_normalizer_uses_legacy_cred_score_fallback():
    raw = {
        "decision": "real",
        "is_real": True,
        "confidence": 0.99,
        "cred_score": 0.72,
    }

    result = normalize_liveness_check(raw)

    assert result["cred_antispoof_score"] == 0.72


def test_liveness_normalizer_fail():
    raw = {
        "decision": "spoof",
        "is_real": False,
        "rejection_reason": "spoof_detected",
    }

    result = normalize_liveness_check(raw)

    assert result["status"] == "failed"
    assert result["decision"] == "deny"
    assert result["reason"] == "spoof_detected"