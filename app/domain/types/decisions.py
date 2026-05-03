from typing import Literal, Optional, TypedDict


PublicDecision = Literal["allow", "deny"]


class ThresholdPolicy(TypedDict):
    type: Literal["minimum_age"]
    value: int
    source: Literal["explicit", "majority_country", "default"]
    majority_country: Optional[str]


class DecisionCheck(TypedDict):
    status: Literal["passed", "failed", "unknown"]
    decision: PublicDecision
    reason: Optional[str]
    threshold: ThresholdPolicy
    cred_decision_score: float


class SpoofCheck(TypedDict):
    status: Literal["passed", "failed", "unknown"]
    decision: PublicDecision
    reason: Optional[str]
    is_real: Optional[bool]
    spoof_detected: Optional[bool]
    cred_antispoof_score: float


class PrivacyMetadata(TypedDict):
    image_stored: bool
    biometric_template_stored: bool
    raw_image_logged: bool
    downstream_raw_response_exposed: bool
    retention_policy: str


class ZkProofMetadata(TypedDict):
    zk_ready: bool
    proof_type: str
    proof_status: str
    statement: str


class VerifyResult(TypedDict, total=False):
    request_id: str
    correlation_id: str
    decision: PublicDecision
    cred_global_score: float
    decision_check: DecisionCheck
    spoof_check: SpoofCheck
    privacy: PrivacyMetadata
    zk_proof: ZkProofMetadata
    reason: Optional[str]
    raw: dict
