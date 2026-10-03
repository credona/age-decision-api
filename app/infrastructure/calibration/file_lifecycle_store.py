import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.domain.calibration.lifecycle import (
    CalibrationLifecycleState,
    CalibrationRollbackRecord,
)
from app.domain.calibration.policy import (
    CalibrationPolicyMetadata,
    RuntimeCalibrationPolicy,
)


class FileCalibrationLifecycleStore:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save_active_policy(self, policy: RuntimeCalibrationPolicy) -> None:
        self._write_policy(self.directory / "active_policy.json", policy)

    def save_previous_policy(self, policy: RuntimeCalibrationPolicy) -> None:
        self._write_policy(self.directory / "previous_policy.json", policy)

    def load_active_policy(self) -> RuntimeCalibrationPolicy | None:
        return self._read_optional_policy(self.directory / "active_policy.json")

    def load_previous_policy(self) -> RuntimeCalibrationPolicy | None:
        return self._read_optional_policy(self.directory / "previous_policy.json")

    def save_state(self, state: CalibrationLifecycleState) -> None:
        self._write_json(self.directory / "lifecycle_state.json", asdict(state))

    def save_rollback_record(self, record: CalibrationRollbackRecord) -> None:
        self._write_json(
            self.directory
            / f"rollback-{record.from_policy_id}-to-{record.to_policy_id}.json",
            asdict(record),
        )

    def load_state(self) -> CalibrationLifecycleState | None:
        path = self.directory / "lifecycle_state.json"

        if not path.is_file():
            return None

        data = self._read_json(path)
        return CalibrationLifecycleState(**data)

    def _write_policy(self, path: Path, policy: RuntimeCalibrationPolicy) -> None:
        self._write_json(
            path,
            {
                "metadata": asdict(policy.metadata),
                "private_payload": dict(policy.private_payload),
            },
        )

    def _read_optional_policy(self, path: Path) -> RuntimeCalibrationPolicy | None:
        if not path.is_file():
            return None

        data = self._read_json(path)
        return RuntimeCalibrationPolicy(
            metadata=CalibrationPolicyMetadata(**data["metadata"]),
            private_payload=data["private_payload"],
        )

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))
