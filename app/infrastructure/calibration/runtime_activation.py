import os

from app.application.calibration.activate_runtime_calibration import (
    ActivateRuntimeCalibrationUseCase,
)
from app.application.calibration.load_runtime_calibration import (
    LoadRuntimeCalibrationUseCase,
)
from app.application.calibration.rollback_runtime_calibration import (
    RollbackRuntimeCalibrationUseCase,
)
from app.domain.calibration import RuntimeCalibrationPolicy
from app.domain.calibration.summary import build_public_calibration_summary
from app.infrastructure.calibration.ed25519_signature_verifier import (
    Ed25519CalibrationSignatureVerifier,
)
from app.infrastructure.calibration.file_attestation_writer import (
    FileCalibrationAttestationWriter,
)
from app.infrastructure.calibration.file_lifecycle_store import (
    FileCalibrationLifecycleStore,
)
from app.infrastructure.calibration.file_manifest_reader import (
    FileCalibrationDistributionManifestReader,
)
from app.infrastructure.calibration.file_policy_reader import (
    FileCalibrationPolicyReader,
)
from app.infrastructure.calibration.file_provenance_store import (
    FileCalibrationProvenanceStore,
)
from app.infrastructure.calibration.file_trusted_registry_reader import (
    FileTrustedCalibrationRegistryReader,
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

    loaded_policy = LoadRuntimeCalibrationUseCase(
        reader=FileCalibrationPolicyReader(calibration_policy_path),
        integrity_verifier=Sha256CalibrationIntegrityVerifier(),
        signature_verifier=Ed25519CalibrationSignatureVerifier(
            calibration_public_key_b64
        ),
    ).execute(
        expected_service="api",
        expected_contract_version=project_metadata.contract_version,
        expected_model_identifier=API_FUSION_MODEL_IDENTIFIER,
    )

    if not _has_lifecycle_configuration():
        return loaded_policy

    return ActivateRuntimeCalibrationUseCase(
        lifecycle_store=FileCalibrationLifecycleStore(
            _required_env("API_CALIBRATION_LIFECYCLE_DIR")
        ),
        manifest_reader=FileCalibrationDistributionManifestReader(
            _required_env("API_CALIBRATION_MANIFEST_PATH")
        ),
        trusted_registry_reader=FileTrustedCalibrationRegistryReader(
            _required_env("API_CALIBRATION_TRUSTED_REGISTRY_PATH")
        ),
        provenance_store=FileCalibrationProvenanceStore(
            _required_env("API_CALIBRATION_PROVENANCE_PATH")
        ),
        attestation_writer=FileCalibrationAttestationWriter(
            _required_env("API_CALIBRATION_ATTESTATION_DIR")
        ),
    ).execute(loaded_policy)


def _has_lifecycle_configuration() -> bool:
    return all(
        os.getenv(name)
        for name in (
            "API_CALIBRATION_LIFECYCLE_DIR",
            "API_CALIBRATION_MANIFEST_PATH",
            "API_CALIBRATION_TRUSTED_REGISTRY_PATH",
            "API_CALIBRATION_PROVENANCE_PATH",
            "API_CALIBRATION_ATTESTATION_DIR",
        )
    )


def _required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"{name}_MISSING")

    return value


def rollback_api_runtime_calibration(
    *,
    reason: str,
) -> RuntimeCalibrationPolicy:
    return RollbackRuntimeCalibrationUseCase(
        lifecycle_store=FileCalibrationLifecycleStore(
            _required_env("API_CALIBRATION_LIFECYCLE_DIR")
        ),
        provenance_store=FileCalibrationProvenanceStore(
            _required_env("API_CALIBRATION_PROVENANCE_PATH")
        ),
        attestation_writer=FileCalibrationAttestationWriter(
            _required_env("API_CALIBRATION_ATTESTATION_DIR")
        ),
    ).execute(reason=reason)


def get_api_runtime_calibration_summary() -> dict[str, str] | None:
    lifecycle_dir = os.getenv("API_CALIBRATION_LIFECYCLE_DIR")

    if not lifecycle_dir:
        return None

    store = FileCalibrationLifecycleStore(lifecycle_dir)
    active_policy = store.load_active_policy()
    state = store.load_state()

    if active_policy is None or state is None:
        return None

    return build_public_calibration_summary(
        policy=active_policy,
        activated_at=state.activated_at,
    )
