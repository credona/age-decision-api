from app.domain.privacy.metadata import build_privacy_metadata
from app.infrastructure.config.settings import settings


def test_privacy_metadata_uses_explicit_downstream_exposure_setting():
    metadata = build_privacy_metadata()

    assert hasattr(settings, "expose_raw_downstream_responses")
    assert metadata["downstream_raw_response_exposed"] is False


def test_privacy_metadata_never_exposes_raw_downstream_responses_by_default():
    metadata = build_privacy_metadata()

    assert metadata["image_stored"] is False
    assert metadata["biometric_template_stored"] is False
    assert metadata["raw_image_logged"] is False
    assert metadata["downstream_raw_response_exposed"] is False
    assert metadata["retention_policy"] == "not_stored_by_api_gateway"
