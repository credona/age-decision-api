from app.normalizers.liveness_normalizer import normalize_liveness_check


def test_liveness_normalizer_pass():
    raw = {
        "decision": "real",
        "is_real": True,
        "confidence": 0.99,
    }

    result = normalize_liveness_check(raw)

    assert result["status"] == "passed"
    assert result["decision"] == "allow"
    assert result["reason"] is None


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