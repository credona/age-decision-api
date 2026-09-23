from app.domain.calibration import (
    ApiFusionCalibrationApplier,
    CalibrationPolicyMetadata,
    RuntimeCalibrationPolicy,
)


def make_policy(private_payload: dict) -> RuntimeCalibrationPolicy:
    return RuntimeCalibrationPolicy(
        metadata=CalibrationPolicyMetadata(
            policy_id="api-policy-test",
            service="api",
            contract_version="2.6",
            policy_version="1.0.0",
            benchmark_attestation_id="attestation-test",
            model_identifier="credona.api.fusion.v1",
            payload_hash="sha256:test",
            signature="signature-test",
        ),
        private_payload=private_payload,
    )


def test_api_fusion_calibration_applier_is_neutral_without_policy() -> None:
    applier = ApiFusionCalibrationApplier()

    result = applier.apply(
        decision="allow",
        cred_global_score=0.8,
        reason=None,
    )

    assert result.decision == "allow"
    assert result.cred_global_score == 0.8
    assert result.reason is None


def test_api_fusion_calibration_applier_applies_private_score_offset() -> None:
    policy = make_policy(
        {
            "calibration_parameters": {
                "cred_global_score_offset": 0.05,
            }
        }
    )

    applier = ApiFusionCalibrationApplier(policy)

    result = applier.apply(
        decision="allow",
        cred_global_score=0.8,
        reason=None,
    )

    assert result.decision == "allow"
    assert result.cred_global_score == 0.85


def test_api_fusion_calibration_applier_applies_floor_and_ceiling() -> None:
    policy = make_policy(
        {
            "calibration_parameters": {
                "cred_global_score_floor": 0.6,
                "cred_global_score_ceiling": 0.9,
            }
        }
    )

    applier = ApiFusionCalibrationApplier(policy)

    low = applier.apply(decision="allow", cred_global_score=0.2, reason=None)
    high = applier.apply(decision="allow", cred_global_score=0.95, reason=None)

    assert low.cred_global_score == 0.6
    assert high.cred_global_score == 0.9


def test_api_fusion_calibration_can_deny_allow_decision_without_exposing_policy() -> (
    None
):
    policy = make_policy(
        {
            "calibration_parameters": {
                "minimum_allow_score": 0.9,
            }
        }
    )

    applier = ApiFusionCalibrationApplier(policy)

    result = applier.apply(
        decision="allow",
        cred_global_score=0.8,
        reason=None,
    )

    assert result.decision == "deny"
    assert result.reason == "verification_failed"
    assert not hasattr(result, "private_payload")
    assert not hasattr(result, "calibration_parameters")


def test_api_fusion_calibration_preserves_inconclusive_decision():
    policy = make_policy(
        {
            "calibration_parameters": {
                "cred_global_score_offset": 0.2,
                "minimum_allow_score": 0.9,
            }
        }
    )
    applier = ApiFusionCalibrationApplier(policy)

    result = applier.apply(
        decision="inconclusive",
        cred_global_score=0.0,
        reason="threshold_uncertain",
    )

    assert result.decision == "inconclusive"
    assert result.reason == "threshold_uncertain"
