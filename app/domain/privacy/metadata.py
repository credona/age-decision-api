from app.infrastructure.config.settings import settings
from app.domain.types import PrivacyMetadata


def build_privacy_metadata() -> PrivacyMetadata:
    """
    Build privacy metadata exposed by the public API.

    The API gateway does not persist images, does not log raw image content
    and does not create biometric templates.
    """
    return {
        "image_stored": False,
        "biometric_template_stored": False,
        "raw_image_logged": False,
        "downstream_raw_response_exposed": settings.expose_raw_downstream_responses,
        "retention_policy": "not_stored_by_api_gateway",
    }
