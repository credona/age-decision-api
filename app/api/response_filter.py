from app.models.schemas import VerifyResponse


def filter_verify_response(payload: dict) -> VerifyResponse:
    """
    Public API contract barrier.

    Internal orchestration data and raw downstream responses are ignored unless
    explicitly declared by the public VerifyResponse schema.
    """
    return VerifyResponse(**payload)
