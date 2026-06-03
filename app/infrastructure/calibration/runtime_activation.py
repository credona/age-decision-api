import os

from app.application.calibration.load_runtime_calibration import (
    LoadRuntimeCalibrationUseCase,
)
from app.domain.calibration import RuntimeCalibrationPolicy
from app.infrastructure.calibration.ed25519_signature_verifier import (
    Ed25519CalibrationSignatureVerifier,
)
from app.infrastructure.calibration.file_policy_reader import (
    FileCalibrationPolicyReader,
)
from app.infrastructure.calibration.sha256_integrity_verifier import (
    Sha256CalibrationIntegrityVerifier,
)
from app.project import project_metadata

API_FUSION_MODEL_IDENTIFIER = "credona.api.fusion.v1"


def _env_bool(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def load_api_runtime_calibration() -> RuntimeCalibrationPolicy | None:
    calibration_required = _env_bool("API_CALIBRATION_REQUIRED", False)
    calibration_policy_path = os.getenv("API_CALIBRATION_POLICY_PATH")
    calibration_public_key_b64 = os.getenv("API_CALIBRATION_PUBLIC_KEY_B64")

    if not calibration_required and not calibration_policy_path:
        return None

    use_case = LoadRuntimeCalibrationUseCase(
        reader=FileCalibrationPolicyReader(calibration_policy_path),
        integrity_verifier=Sha256CalibrationIntegrityVerifier(),
        signature_verifier=Ed25519CalibrationSignatureVerifier(
            calibration_public_key_b64
        ),
    )

    return use_case.execute(
        expected_service="api",
        expected_contract_version=project_metadata.contract_version,
        expected_model_identifier=API_FUSION_MODEL_IDENTIFIER,
    )
