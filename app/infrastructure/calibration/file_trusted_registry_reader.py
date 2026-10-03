import json
from pathlib import Path

from app.domain.calibration.errors import CalibrationActivationError
from app.domain.calibration.policy import RuntimeCalibrationPolicy


class FileTrustedCalibrationRegistryReader:
    def __init__(self, path: str | None):
        self.path = path

    def assert_policy_trusted(self, policy: RuntimeCalibrationPolicy) -> None:
        if not self.path:
            raise CalibrationActivationError(
                "CALIBRATION_TRUSTED_REGISTRY_PATH_MISSING"
            )

        registry_path = Path(self.path)
        if not registry_path.is_file():
            raise CalibrationActivationError(
                "CALIBRATION_TRUSTED_REGISTRY_FILE_MISSING"
            )

        document = json.loads(registry_path.read_text(encoding="utf-8"))

        if document.get("service") != policy.metadata.service:
            raise CalibrationActivationError(
                "CALIBRATION_TRUSTED_REGISTRY_WRONG_SERVICE"
            )

        trusted_policies = document.get("trusted_policies", [])
        for trusted_policy in trusted_policies:
            if (
                trusted_policy.get("policy_id") == policy.metadata.policy_id
                and trusted_policy.get("payload_hash") == policy.metadata.payload_hash
                and trusted_policy.get("model_identifier")
                == policy.metadata.model_identifier
            ):
                return

        raise CalibrationActivationError("CALIBRATION_POLICY_NOT_TRUSTED")
