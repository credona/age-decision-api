import json
from pathlib import Path

from app.domain.calibration.policy import RuntimeCalibrationPolicy


class FileCalibrationAttestationWriter:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def write_activation_attestation(
        self,
        *,
        policy: RuntimeCalibrationPolicy,
        activated_at: str,
    ) -> Path:
        path = self.directory / f"activation-{policy.metadata.policy_id}.json"
        self._write_attestation(
            path=path,
            policy=policy,
            event_type="activation",
            event_at=activated_at,
        )
        return path

    def write_rollback_attestation(
        self,
        *,
        policy: RuntimeCalibrationPolicy,
        rolled_back_at: str,
    ) -> Path:
        path = self.directory / f"rollback-{policy.metadata.policy_id}.json"
        self._write_attestation(
            path=path,
            policy=policy,
            event_type="rollback",
            event_at=rolled_back_at,
        )
        return path

    def _write_attestation(
        self,
        *,
        path: Path,
        policy: RuntimeCalibrationPolicy,
        event_type: str,
        event_at: str,
    ) -> None:
        payload = {
            "event_type": event_type,
            "event_at": event_at,
            "service": policy.metadata.service,
            "contract_version": policy.metadata.contract_version,
            "model_identifier": policy.metadata.model_identifier,
            "policy_id": policy.metadata.policy_id,
            "policy_version": policy.metadata.policy_version,
            "benchmark_attestation_id": policy.metadata.benchmark_attestation_id,
        }
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
