import json
from pathlib import Path

from app.application.calibration.activate_runtime_calibration import (
    ActivateRuntimeCalibrationUseCase,
)
from app.domain.calibration.lifecycle import CalibrationLifecycleState
from app.domain.calibration.policy import (
    CalibrationPolicyMetadata,
    RuntimeCalibrationPolicy,
)


class MemoryLifecycleStore:
    def __init__(self, previous_policy: RuntimeCalibrationPolicy | None = None):
        self.active_policy: RuntimeCalibrationPolicy | None = None
        self.previous_policy = previous_policy
        self.state: CalibrationLifecycleState | None = None

    def save_active_policy(self, policy: RuntimeCalibrationPolicy) -> None:
        self.active_policy = policy

    def save_previous_policy(self, policy: RuntimeCalibrationPolicy) -> None:
        self.previous_policy = policy

    def load_active_policy(self) -> RuntimeCalibrationPolicy | None:
        return self.active_policy

    def load_previous_policy(self) -> RuntimeCalibrationPolicy | None:
        return self.previous_policy

    def save_state(self, state: CalibrationLifecycleState) -> None:
        self.state = state


class RecordingManifestReader:
    def __init__(self):
        self.validated_policy_id: str | None = None

    def assert_policy_allowed(self, policy: RuntimeCalibrationPolicy) -> None:
        self.validated_policy_id = policy.metadata.policy_id


class RecordingTrustedRegistryReader:
    def __init__(self):
        self.validated_policy_id: str | None = None

    def assert_policy_trusted(self, policy: RuntimeCalibrationPolicy) -> None:
        self.validated_policy_id = policy.metadata.policy_id


class MemoryProvenanceStore:
    def __init__(self):
        self.events = []

    def append(self, event) -> None:
        self.events.append(event)


class MemoryAttestationWriter:
    def __init__(self, directory: Path):
        self.directory = directory
        self.activation_policy_id: str | None = None

    def write_activation_attestation(
        self,
        *,
        policy: RuntimeCalibrationPolicy,
        activated_at: str,
    ) -> Path:
        self.activation_policy_id = policy.metadata.policy_id
        path = self.directory / "activation-test.json"
        path.write_text(json.dumps({"policy_id": policy.metadata.policy_id}))
        return path


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


def test_activate_runtime_calibration_validates_persists_and_attests(
    tmp_path: Path,
) -> None:
    new_policy = make_policy("new-policy")
    previous_policy = make_policy("previous-policy")

    lifecycle_store = MemoryLifecycleStore(previous_policy=previous_policy)
    manifest_reader = RecordingManifestReader()
    trusted_registry_reader = RecordingTrustedRegistryReader()
    provenance_store = MemoryProvenanceStore()
    attestation_writer = MemoryAttestationWriter(tmp_path)

    activated_policy = ActivateRuntimeCalibrationUseCase(
        lifecycle_store=lifecycle_store,
        manifest_reader=manifest_reader,
        trusted_registry_reader=trusted_registry_reader,
        provenance_store=provenance_store,
        attestation_writer=attestation_writer,
        clock=lambda: "2026-06-04T00:00:00Z",
    ).execute(new_policy)

    assert activated_policy.metadata.policy_id == "new-policy"

    assert manifest_reader.validated_policy_id == "new-policy"
    assert trusted_registry_reader.validated_policy_id == "new-policy"

    assert lifecycle_store.previous_policy is previous_policy
    assert lifecycle_store.active_policy is new_policy
    assert lifecycle_store.state is not None
    assert lifecycle_store.state.active_policy_id == "new-policy"
    assert lifecycle_store.state.previous_policy_id == "previous-policy"

    assert len(provenance_store.events) == 1
    assert provenance_store.events[0].event_type == "activation"
    assert provenance_store.events[0].policy_id == "new-policy"

    assert attestation_writer.activation_policy_id == "new-policy"
