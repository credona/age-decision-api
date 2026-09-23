from pathlib import Path

from app.application.calibration.rollback_runtime_calibration import (
    RollbackRuntimeCalibrationUseCase,
)
from app.domain.calibration.lifecycle import CalibrationLifecycleState
from app.domain.calibration.policy import (
    CalibrationPolicyMetadata,
    RuntimeCalibrationPolicy,
)


class MemoryLifecycleStore:
    def __init__(
        self,
        active_policy: RuntimeCalibrationPolicy,
        previous_policy: RuntimeCalibrationPolicy,
    ):
        self.active_policy = active_policy
        self.previous_policy = previous_policy
        self.state: CalibrationLifecycleState | None = None
        self.saved_active_policy: RuntimeCalibrationPolicy | None = None
        self.rollback_record = None

    def load_active_policy(self) -> RuntimeCalibrationPolicy | None:
        return self.active_policy

    def load_previous_policy(self) -> RuntimeCalibrationPolicy | None:
        return self.previous_policy

    def save_active_policy(self, policy: RuntimeCalibrationPolicy) -> None:
        self.saved_active_policy = policy
        self.active_policy = policy

    def save_state(self, state: CalibrationLifecycleState) -> None:
        self.state = state

    def save_rollback_record(self, record) -> None:
        self.rollback_record = record


class MemoryProvenanceStore:
    def __init__(self):
        self.events = []

    def append(self, event) -> None:
        self.events.append(event)


class MemoryAttestationWriter:
    def __init__(self, directory: Path):
        self.directory = directory
        self.rollback_policy_id: str | None = None

    def write_rollback_attestation(
        self,
        *,
        policy: RuntimeCalibrationPolicy,
        rolled_back_at: str,
    ) -> Path:
        self.rollback_policy_id = policy.metadata.policy_id
        return self.directory / "rollback-test.json"


def make_policy(policy_id: str) -> RuntimeCalibrationPolicy:
    return RuntimeCalibrationPolicy(
        metadata=CalibrationPolicyMetadata(
            policy_id=policy_id,
            service="api",
            contract_version="2.6",
            policy_version="1.0.0",
            benchmark_attestation_id="benchmark-attestation-api",
            model_identifier="credona.api.fusion.v1",
            payload_hash=f"sha256:{policy_id}",
            signature="private-signature",
        ),
        private_payload={
            "calibration_parameters": {
                "cred_global_score_offset": 0.1,
            }
        },
    )


def test_rollback_runtime_calibration_restores_previous_policy_and_attests(
    tmp_path: Path,
) -> None:
    active = make_policy("active-policy")
    previous = make_policy("previous-policy")

    lifecycle_store = MemoryLifecycleStore(
        active_policy=active,
        previous_policy=previous,
    )
    provenance_store = MemoryProvenanceStore()
    attestation_writer = MemoryAttestationWriter(tmp_path)

    rolled_back_policy = RollbackRuntimeCalibrationUseCase(
        lifecycle_store=lifecycle_store,
        provenance_store=provenance_store,
        attestation_writer=attestation_writer,
        clock=lambda: "2026-06-04T00:00:00Z",
    ).execute(reason="manual_rollback")

    assert rolled_back_policy.metadata.policy_id == "previous-policy"
    assert lifecycle_store.saved_active_policy is previous
    assert lifecycle_store.state is not None
    assert lifecycle_store.state.active_policy_id == "previous-policy"
    assert lifecycle_store.state.previous_policy_id == "active-policy"

    assert lifecycle_store.rollback_record is not None
    assert lifecycle_store.rollback_record.from_policy_id == "active-policy"
    assert lifecycle_store.rollback_record.to_policy_id == "previous-policy"

    assert len(provenance_store.events) == 1
    assert provenance_store.events[0].event_type == "rollback"
    assert provenance_store.events[0].policy_id == "previous-policy"

    assert attestation_writer.rollback_policy_id == "previous-policy"
