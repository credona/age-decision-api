from app.models.schemas import CalibrationSummaryResponse, VerifyResponse


def filter_verify_response(payload: dict) -> VerifyResponse:
    """
    Public API contract barrier.

    Internal orchestration data and raw downstream responses are ignored unless
    explicitly declared by the public VerifyResponse schema.
    """
    return VerifyResponse(**payload)


def filter_calibration_summary_response(
    payload: dict | None,
) -> CalibrationSummaryResponse:
    if payload is None:
        return CalibrationSummaryResponse(active=False, summary=None)

    return CalibrationSummaryResponse(
        active=True,
        summary=payload,
    )
