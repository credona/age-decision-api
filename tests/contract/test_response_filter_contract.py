from app.api.response_filter import filter_verify_response


def test_verify_response_filter_ignores_internal_fields():
    response = filter_verify_response(
        {
            "request_id": "req-1",
            "correlation_id": "corr-1",
            "decision": "allow",
            "cred_global_score": 0.82,
            "decision_check": {
                "status": "passed",
                "decision": "allow",
                "reason": None,
                "threshold": {
                    "type": "minimum_age",
                    "value": 18,
                    "source": "default",
                    "majority_country": None,
                },
                "cred_decision_score": 0.84,
            },
            "spoof_check": {
                "status": "passed",
                "decision": "allow",
                "reason": None,
                "is_real": True,
                "spoof_detected": False,
                "cred_antispoof_score": 0.82,
            },
            "privacy": {
                "image_stored": False,
                "biometric_template_stored": False,
                "raw_image_logged": False,
                "downstream_raw_response_exposed": False,
                "retention_policy": "none",
            },
            "zk_proof": {
                "zk_ready": True,
                "proof_type": "metadata",
                "proof_status": "not_generated",
                "statement": "age_and_liveness_thresholds_satisfied",
            },
            "reason": None,
            "estimated_age": 25,
            "confidence": 0.99,
            "raw_scores": {"core": 0.9},
            "internal_thresholds": {"age": 18},
            "raw": {
                "core": {"estimated_age": 25},
                "antispoof": {"raw_scores": [0.1, 0.9]},
            },
        }
    )

    dumped = response.model_dump()

    assert "estimated_age" not in dumped
    assert "confidence" not in dumped
    assert "raw_scores" not in dumped
    assert "internal_thresholds" not in dumped
    assert "raw" not in dumped
