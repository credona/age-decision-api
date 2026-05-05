import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """
    Application settings loaded from environment variables.
    """

    api_description: str = os.getenv(
        "API_DESCRIPTION",
        "Public API gateway for Age Decision services.",
    )
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "info")

    age_decision_core_url: str = os.getenv(
        "AGE_DECISION_CORE_URL",
        "http://age-decision-core:8000",
    )

    age_decision_antispoof_url: str = os.getenv(
        "AGE_DECISION_ANTISPOOF_URL",
        "http://age-decision-antispoof:8001",
    )

    request_timeout_ms: int = int(os.getenv("REQUEST_TIMEOUT", "3000"))

    expose_raw_downstream_responses: bool = (
        os.getenv("EXPOSE_RAW_DOWNSTREAM_RESPONSES", "false").lower() == "true"
    )

    @property
    def request_timeout_seconds(self) -> float:
        return self.request_timeout_ms / 1000


settings = Settings()
