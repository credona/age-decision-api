from app.api.response_filter import filter_verify_response

FORBIDDEN_CALIBRATION_FIELDS = (
    "calibration_parameters",
    "cred_global_score_offset",
    "cred_global_score_floor",
    "cred_global_score_ceiling",
    "minimum_allow_score",
    "private_payload",
    "weights",
    "margins",
    "calibration_internals",
    "signature",
    "payload_hash",
    "policy_id",
)


def test_response_filter_strips_runtime_calibration_private_fields() -> None:
    response = filter_verify_response(
        {
            "request_id": "req-1",
            "correlation_id": "corr-1",
            "decision": "deny",
            "cred_global_score": 0.42,
            "reason": "verification_failed",
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
                "reason": "spoof_check_failed",
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
                "statement": "age_and_liveness_thresholds_satisfied",
            },
            "private_payload": {
                "calibration_parameters": {
                    "cred_global_score_offset": 0.1,
                    "minimum_allow_score": 0.85,
                    "weights": {"private": 0.4},
                    "margins": {"private": 2},
                }
            },
            "calibration_internals": {
                "thresholds": [0.5],
                "weights": [0.4],
                "margins": [2],
            },
            "policy_id": "api-private-policy",
            "signature": "private-signature",
            "payload_hash": "sha256:private",
        }
    )

    serialized = response.model_dump_json()

    for forbidden in FORBIDDEN_CALIBRATION_FIELDS:
        assert forbidden not in serialized
