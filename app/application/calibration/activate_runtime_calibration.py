from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

from app.domain.calibration.lifecycle import CalibrationLifecycleState
from app.domain.calibration.policy import RuntimeCalibrationPolicy
from app.domain.calibration.provenance import CalibrationProvenanceEvent


class CalibrationLifecycleStorePort(Protocol):
    def save_active_policy(self, policy: RuntimeCalibrationPolicy) -> None: ...

    def save_previous_policy(self, policy: RuntimeCalibrationPolicy) -> None: ...

    def load_active_policy(self) -> RuntimeCalibrationPolicy | None: ...

    def load_previous_policy(self) -> RuntimeCalibrationPolicy | None: ...

    def save_state(self, state: CalibrationLifecycleState) -> None: ...


class CalibrationManifestReaderPort(Protocol):
    def assert_policy_allowed(self, policy: RuntimeCalibrationPolicy) -> None: ...


class TrustedCalibrationRegistryReaderPort(Protocol):
    def assert_policy_trusted(self, policy: RuntimeCalibrationPolicy) -> None: ...


class CalibrationProvenanceStorePort(Protocol):
    def append(self, event: CalibrationProvenanceEvent) -> None: ...


class CalibrationAttestationWriterPort(Protocol):
    def write_activation_attestation(
        self,
        *,
        policy: RuntimeCalibrationPolicy,
        activated_at: str,
    ) -> object: ...


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class ActivateRuntimeCalibrationUseCase:
    def __init__(
        self,
        *,
        lifecycle_store: CalibrationLifecycleStorePort,
        manifest_reader: CalibrationManifestReaderPort,
        trusted_registry_reader: TrustedCalibrationRegistryReaderPort,
        provenance_store: CalibrationProvenanceStorePort,
        attestation_writer: CalibrationAttestationWriterPort,
        clock: Callable[[], str] = utc_now_iso,
    ):
        self.lifecycle_store = lifecycle_store
        self.manifest_reader = manifest_reader
        self.trusted_registry_reader = trusted_registry_reader
        self.provenance_store = provenance_store
        self.attestation_writer = attestation_writer
        self.clock = clock

    def execute(
        self,
        policy: RuntimeCalibrationPolicy,
    ) -> RuntimeCalibrationPolicy:
        activated_at = self.clock()

        self.manifest_reader.assert_policy_allowed(policy)
        self.trusted_registry_reader.assert_policy_trusted(policy)

        previous_policy = self.lifecycle_store.load_previous_policy()

        if previous_policy is None:
            previous_policy = self.lifecycle_store.load_active_policy()

        if previous_policy is not None:
            self.lifecycle_store.save_previous_policy(previous_policy)

        state = CalibrationLifecycleState.activate(
            active_policy=policy,
            previous_policy=previous_policy,
            activated_at=activated_at,
        )

        self.lifecycle_store.save_active_policy(policy)
        self.lifecycle_store.save_state(state)

        event = CalibrationProvenanceEvent.create(
            event_type="activation",
            policy=policy,
            created_at=activated_at,
            previous_hash=None,
        )

        self.provenance_store.append(event)
        self.attestation_writer.write_activation_attestation(
            policy=policy,
            activated_at=activated_at,
        )

        return policy
