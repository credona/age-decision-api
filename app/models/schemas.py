from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    service: str = Field(..., examples=["age-decision-api"])
    version: str = Field(..., examples=["2.1.0"])
    contract_version: str = Field(..., examples=["2.0"])


class ServiceReadyStatus(BaseModel):
    status: Literal["ready", "unavailable"]
    url: str


class ReadyResponse(BaseModel):
    status: Literal["ready", "degraded"]
    service: str
    version: str
    contract_version: str
    core: ServiceReadyStatus
    antispoof: ServiceReadyStatus


class VerifyRequest(BaseModel):
    input_type: Literal["image", "image_sequence", "video"] = Field(default="image")
    image_base64: str = Field(..., min_length=1)
    majority_country: Optional[str] = Field(default=None, examples=["FR", "US"])
    age_threshold: Optional[int] = Field(default=None, examples=[18, 21])


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    request_id: str
    correlation_id: str
    error: ErrorDetail


class ThresholdPolicy(BaseModel):
    type: Literal["minimum_age"]
    value: int
    source: Literal["explicit", "majority_country", "default"]
    majority_country: Optional[str] = None


class NormalizedCheckResponse(BaseModel):
    status: Literal["passed", "failed", "unknown"]
    decision: Literal["allow", "deny"]
    reason: Optional[str] = None


class DecisionCheckResponse(NormalizedCheckResponse):
    threshold: ThresholdPolicy
    cred_decision_score: float


class SpoofCheckResponse(NormalizedCheckResponse):
    is_real: Optional[bool] = None
    spoof_detected: Optional[bool] = None
    cred_antispoof_score: float


class PrivacyMetadataResponse(BaseModel):
    image_stored: bool
    biometric_template_stored: bool
    raw_image_logged: bool
    downstream_raw_response_exposed: bool
    retention_policy: str


class ZkProofMetadataResponse(BaseModel):
    zk_ready: bool
    proof_type: str
    proof_status: str
    statement: str


class VerifyResponse(BaseModel):
    request_id: str
    correlation_id: str
    decision: Literal["allow", "deny"]
    cred_global_score: float
    decision_check: DecisionCheckResponse
    spoof_check: SpoofCheckResponse
    privacy: PrivacyMetadataResponse
    zk_proof: ZkProofMetadataResponse
    reason: Optional[str] = None
    raw: Optional[dict[str, Any]] = Field(default=None, exclude=True)
