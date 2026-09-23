from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

from app.domain.calibration.errors import CalibrationActivationError
from app.domain.calibration.lifecycle import (
    CalibrationLifecycleState,
    CalibrationRollbackRecord,
)
from app.domain.calibration.policy import RuntimeCalibrationPolicy
from app.domain.calibration.provenance import CalibrationProvenanceEvent


class CalibrationRollbackLifecycleStorePort(Protocol):
    def load_active_policy(self) -> RuntimeCalibrationPolicy | None: ...

    def load_previous_policy(self) -> RuntimeCalibrationPolicy | None: ...

    def save_active_policy(self, policy: RuntimeCalibrationPolicy) -> None: ...

    def save_state(self, state: CalibrationLifecycleState) -> None: ...

    def save_rollback_record(self, record: CalibrationRollbackRecord) -> None: ...


class CalibrationRollbackProvenanceStorePort(Protocol):
    def append(self, event: CalibrationProvenanceEvent) -> None: ...


class CalibrationRollbackAttestationWriterPort(Protocol):
    def write_rollback_attestation(
        self,
        *,
        policy: RuntimeCalibrationPolicy,
        rolled_back_at: str,
    ) -> object: ...


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class RollbackRuntimeCalibrationUseCase:
    def __init__(
        self,
        *,
        lifecycle_store: CalibrationRollbackLifecycleStorePort,
        provenance_store: CalibrationRollbackProvenanceStorePort,
        attestation_writer: CalibrationRollbackAttestationWriterPort,
        clock: Callable[[], str] = utc_now_iso,
    ):
        self.lifecycle_store = lifecycle_store
        self.provenance_store = provenance_store
        self.attestation_writer = attestation_writer
        self.clock = clock

    def execute(self, *, reason: str) -> RuntimeCalibrationPolicy:
        rolled_back_at = self.clock()

        active_policy = self.lifecycle_store.load_active_policy()
        previous_policy = self.lifecycle_store.load_previous_policy()

        if active_policy is None:
            raise CalibrationActivationError("CALIBRATION_ACTIVE_POLICY_MISSING")

        if previous_policy is None:
            raise CalibrationActivationError("CALIBRATION_PREVIOUS_POLICY_MISSING")

        record = CalibrationRollbackRecord.create(
            from_policy=active_policy,
            to_policy=previous_policy,
            rolled_back_at=rolled_back_at,
            reason=reason,
        )

        state = CalibrationLifecycleState.activate(
            active_policy=previous_policy,
            previous_policy=active_policy,
            activated_at=rolled_back_at,
        )

        if hasattr(self.lifecycle_store, "save_previous_policy"):
            self.lifecycle_store.save_previous_policy(active_policy)

        self.lifecycle_store.save_active_policy(previous_policy)
        self.lifecycle_store.save_state(state)
        self.lifecycle_store.save_rollback_record(record)

        event = CalibrationProvenanceEvent.create(
            event_type="rollback",
            policy=previous_policy,
            created_at=rolled_back_at,
            previous_hash=None,
        )
        self.provenance_store.append(event)

        self.attestation_writer.write_rollback_attestation(
            policy=previous_policy,
            rolled_back_at=rolled_back_at,
        )

        return previous_policy
