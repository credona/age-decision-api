from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyCommand:
    image_base64: str
    request_id: str
    correlation_id: str
    majority_country: str | None
    age_threshold: int | None
