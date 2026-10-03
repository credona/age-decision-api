from app.api.response_filter import filter_verify_response


def test_verify_response_filter_strips_internal_payloads():
    response = filter_verify_response(
        {
            "request_id": "req-1",
            "correlation_id": "corr-1",
            "decision": "deny",
            "cred_global_score": 0.42,
            "reason": "spoof_check_failed",
            "decision_check": {
                "status": "passed",
                "decision": "allow",
                "reason": None,
                "threshold": {
                    "type": "minimum_age",
                    "value": 18,
                    "source": "majority_country",
                    "majority_country": "FR",
                },
                "cred_decision_score": 0.9,
            },
            "spoof_check": {
                "status": "failed",
                "decision": "deny",
                "reason": "spoof_detected",
                "is_real": False,
                "spoof_detected": True,
                "cred_antispoof_score": 0.3,
            },
            "privacy": {
                "image_stored": False,
                "biometric_template_stored": False,
                "raw_image_logged": False,
                "downstream_raw_response_exposed": False,
                "retention_policy": "not_stored_by_api_gateway",
            },
            "zk_proof": {
                "zk_ready": True,
                "proof_type": "interactive_zero_knowledge_ready",
                "proof_status": "not_generated",
                "statement": "The API is ready to prove a threshold decision without exposing the raw image, estimated age, or raw model scores.",
            },
            "raw": {"estimated_age": 17.2},
            "downstream_response": {"confidence": 0.91},
            "internal_thresholds": {"age": 18},
        }
    )

    payload = response.model_dump()

    assert "raw" not in payload
    assert "downstream_response" not in payload
    assert "internal_thresholds" not in payload
