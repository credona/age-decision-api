from dataclasses import dataclass

from app.domain.calibration.policy import RuntimeCalibrationPolicy


@dataclass(frozen=True)
class CalibrationLifecycleState:
    active_policy_id: str
    previous_policy_id: str | None
    active_payload_hash: str
    previous_payload_hash: str | None
    service: str
    contract_version: str
    model_identifier: str
    activated_at: str

    @classmethod
    def activate(
        cls,
        *,
        active_policy: RuntimeCalibrationPolicy,
        previous_policy: RuntimeCalibrationPolicy | None,
        activated_at: str,
    ) -> "CalibrationLifecycleState":
        return cls(
            active_policy_id=active_policy.metadata.policy_id,
            previous_policy_id=previous_policy.metadata.policy_id
            if previous_policy
            else None,
            active_payload_hash=active_policy.metadata.payload_hash,
            previous_payload_hash=previous_policy.metadata.payload_hash
            if previous_policy
            else None,
            service=active_policy.metadata.service,
            contract_version=active_policy.metadata.contract_version,
            model_identifier=active_policy.metadata.model_identifier,
            activated_at=activated_at,
        )


@dataclass(frozen=True)
class CalibrationRollbackRecord:
    from_policy_id: str
    to_policy_id: str
    service: str
    contract_version: str
    model_identifier: str
    rolled_back_at: str
    reason: str

    @classmethod
    def create(
        cls,
        *,
        from_policy: RuntimeCalibrationPolicy,
        to_policy: RuntimeCalibrationPolicy,
        rolled_back_at: str,
        reason: str,
    ) -> "CalibrationRollbackRecord":
        return cls(
            from_policy_id=from_policy.metadata.policy_id,
            to_policy_id=to_policy.metadata.policy_id,
            service=to_policy.metadata.service,
            contract_version=to_policy.metadata.contract_version,
            model_identifier=to_policy.metadata.model_identifier,
            rolled_back_at=rolled_back_at,
            reason=reason,
        )
