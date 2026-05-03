from app.domain.constants import PROOF_STATUS_NOT_GENERATED, PROOF_TYPE_ZK_READY


def build_zk_proof_metadata() -> dict:
    """
    Build ZK-ready metadata.

    This does not generate a cryptographic proof.
    It only preserves a future-compatible response structure.
    """
    return {
        "zk_ready": True,
        "proof_type": PROOF_TYPE_ZK_READY,
        "proof_status": PROOF_STATUS_NOT_GENERATED,
        "statement": "The API is ready to prove a threshold decision without exposing the raw image, estimated age, or raw model scores.",
    }
