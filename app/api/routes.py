from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException

from app.config.settings import settings
from app.models.schemas import HealthResponse, ReadyResponse, VerifyRequest, VerifyResponse
from app.services.decision_service import decision_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Basic health endpoint.

    It only confirms that the API process is running.
    """
    return HealthResponse(
        status="ok",
        service=settings.app_name,
    )


@router.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    """
    Readiness endpoint.

    It checks whether downstream services are reachable.
    """
    statuses = await decision_service.readiness()

    global_status = (
        "ready"
        if statuses["core"]["status"] == "ready"
        and statuses["antispoof"]["status"] == "ready"
        else "degraded"
    )

    return ReadyResponse(
        status=global_status,
        service=settings.app_name,
        core=statuses["core"],
        antispoof=statuses["antispoof"],
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify(
    payload: VerifyRequest,
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
) -> VerifyResponse:
    """
    Public image verification endpoint.

    V1.1 accepts a base64 image payload and orchestrates:
    - age-decision-core /estimate
    - age-decision-antispoof /check
    - consolidated decision
    - global cred score
    - privacy metadata
    - ZK-ready metadata
    """
    request_id = x_request_id or str(uuid4())
    correlation_id = x_correlation_id or request_id

    try:
        result = await decision_service.verify_image_base64(
            image_base64=payload.image_base64,
            request_id=request_id,
            correlation_id=correlation_id,
            country=payload.country,
            age_threshold=payload.age_threshold,
            age_margin=payload.age_margin,
            confidence_threshold=payload.confidence_threshold,
        )
        return VerifyResponse(**result)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "request_id": request_id,
                "correlation_id": correlation_id,
                "error": str(exc),
            },
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "request_id": request_id,
                "correlation_id": correlation_id,
                "error": "downstream_service_error",
                "message": str(exc),
            },
        ) from exc