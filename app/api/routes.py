from uuid import uuid4

from fastapi import APIRouter, Header, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models.schemas import (
    ErrorResponse,
    HealthResponse,
    ReadyResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.project import project_metadata
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
        service=project_metadata.service_name,
        version=project_metadata.version,
        contract_version=project_metadata.contract_version,
    )


@router.get("/version")
def version():
    """
    Return service version metadata.
    """
    return project_metadata.model_dump()


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
        service=project_metadata.service_name,
        version=project_metadata.version,
        contract_version=project_metadata.contract_version,
        core=statuses["core"],
        antispoof=statuses["antispoof"],
    )


@router.post(
    "/verify",
    response_model=VerifyResponse,
    responses={
        400: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
    },
)
async def verify(
    payload: VerifyRequest,
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
):
    """
    Public image verification endpoint.

    It accepts a base64 image payload and orchestrates:
    - age-decision-core /estimate
    - age-decision-antispoof /check
    - consolidated decision
    - global Credona score
    - privacy metadata
    - ZK-ready metadata
    """
    request_id, correlation_id = _resolve_request_identifiers(
        x_request_id=x_request_id,
        x_correlation_id=x_correlation_id,
    )

    try:
        result = await decision_service.verify_image_base64(
            image_base64=payload.image_base64,
            request_id=request_id,
            correlation_id=correlation_id,
            majority_country=payload.majority_country,
            age_threshold=payload.age_threshold,
        )
        return VerifyResponse(**result)

    except ValueError:
        decision_service.log_event(
            event="verification_rejected",
            request_id=request_id,
            correlation_id=correlation_id,
            extra_data={
                "error_type": "validation_error",
                "error_code": "invalid_base64_image",
            },
        )

        return _error_response(
            status_code=400,
            request_id=request_id,
            correlation_id=correlation_id,
            code="invalid_base64_image",
            message="Invalid request.",
        )

    except Exception:
        decision_service.log_event(
            event="verification_failed",
            request_id=request_id,
            correlation_id=correlation_id,
            extra_data={
                "error_type": "downstream_error",
                "error_code": "downstream_service_error",
            },
        )

        return _error_response(
            status_code=502,
            request_id=request_id,
            correlation_id=correlation_id,
            code="downstream_service_error",
            message="An upstream service error has occurred.",
        )


async def handle_request_validation_error(
    request: Request, exc: RequestValidationError
):
    errors = exc.errors()
    scope_path = request.scope.get("path")

    if scope_path != "/verify" or not _should_normalize_verify_validation_errors(
        errors
    ):
        return await request_validation_exception_handler(request, exc)

    request_id, correlation_id = _resolve_request_identifiers(
        x_request_id=request.headers.get("x-request-id"),
        x_correlation_id=request.headers.get("x-correlation-id"),
    )
    error_code = _map_validation_error_code(errors)

    decision_service.log_event(
        event="verification_rejected",
        request_id=request_id,
        correlation_id=correlation_id,
        extra_data={
            "error_type": "validation_error",
            "error_code": error_code,
        },
    )

    return _error_response(
        status_code=400,
        request_id=request_id,
        correlation_id=correlation_id,
        code=error_code,
        message="Invalid request.",
    )


def _should_normalize_verify_validation_errors(errors: list[dict]) -> bool:
    """Only JSON bodies that decode and fail field-level VerifyRequest checks."""
    for error in errors:
        loc_labels = tuple(str(part) for part in error.get("loc", ()))
        if not loc_labels or loc_labels[0] != "body":
            continue
        if len(loc_labels) >= 2:
            return True
    return False


def _error_response(
    status_code: int,
    request_id: str,
    correlation_id: str,
    code: str,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "request_id": request_id,
            "correlation_id": correlation_id,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def _resolve_request_identifiers(
    x_request_id: str | None,
    x_correlation_id: str | None,
) -> tuple[str, str]:
    request_id = x_request_id or str(uuid4())
    correlation_id = x_correlation_id or request_id
    return request_id, correlation_id


def _map_validation_error_code(errors: list[dict]) -> str:
    for error in errors:
        loc = error.get("loc", ())
        error_type = error.get("type", "")

        loc_labels = tuple(str(part) for part in loc)

        if "image_base64" in loc_labels and error_type in {
            "missing",
            "value_error.missing",
        }:
            return "missing_image_base64"

    return "invalid_request"
