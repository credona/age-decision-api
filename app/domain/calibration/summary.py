from app.domain.calibration.policy import RuntimeCalibrationPolicy


def build_public_calibration_summary(
    *,
    policy: RuntimeCalibrationPolicy,
    activated_at: str,
) -> dict[str, str]:
    return {
        "service": policy.metadata.service,
        "contract_version": policy.metadata.contract_version,
        "model_identifier": policy.metadata.model_identifier,
        "policy_id": policy.metadata.policy_id,
        "policy_version": policy.metadata.policy_version,
        "benchmark_attestation_id": policy.metadata.benchmark_attestation_id,
        "activated_at": activated_at,
    }
