import json
from pathlib import Path

from app.domain.calibration.errors import CalibrationActivationError
from app.domain.calibration.policy import RuntimeCalibrationPolicy


class FileCalibrationDistributionManifestReader:
    def __init__(self, path: str | None):
        self.path = path

    def assert_policy_allowed(self, policy: RuntimeCalibrationPolicy) -> None:
        if not self.path:
            raise CalibrationActivationError("CALIBRATION_MANIFEST_PATH_MISSING")

        manifest_path = Path(self.path)
        if not manifest_path.is_file():
            raise CalibrationActivationError("CALIBRATION_MANIFEST_FILE_MISSING")

        document = json.loads(manifest_path.read_text(encoding="utf-8"))

        if document.get("service") != policy.metadata.service:
            raise CalibrationActivationError("CALIBRATION_MANIFEST_WRONG_SERVICE")

        if document.get("contract_version") != policy.metadata.contract_version:
            raise CalibrationActivationError(
                "CALIBRATION_MANIFEST_WRONG_CONTRACT_VERSION"
            )

        trusted_policy_ids = document.get("trusted_policy_ids", [])
        if policy.metadata.policy_id not in trusted_policy_ids:
            raise CalibrationActivationError("CALIBRATION_POLICY_NOT_IN_MANIFEST")
