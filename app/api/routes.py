from uuid import uuid4

from fastapi import APIRouter, Header, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.input_validator import UnsupportedInputTypeError, validate_input_type
from app.api.response_filter import filter_verify_response
from app.application.dto.verify_command import VerifyCommand
from app.application.use_cases.run_verification import RunVerificationUseCase
from app.application.use_cases.verification_orchestrator import (
    verification_orchestrator,
)
from app.domain.constants import (
    ERROR_DOWNSTREAM,
    ERROR_INVALID_BASE64,
    ERROR_INVALID_REQUEST,
    ERROR_MISSING_IMAGE,
    LOG_ERROR_TYPE_DOWNSTREAM,
    LOG_ERROR_TYPE_VALIDATION,
    STATUS_READY,
)
from app.infrastructure.clients.antispoof_client import antispoof_client
from app.infrastructure.clients.core_client import core_client
from app.models.schemas import (
    ErrorResponse,
    HealthResponse,
    ReadyResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.project import project_metadata

router = APIRouter()

verification_orchestrator.core_client = core_client
verification_orchestrator.antispoof_client = antispoof_client
run_verification_use_case = RunVerificationUseCase(verification_orchestrator)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=project_metadata.service_name,
        version=project_metadata.version,
        contract_version=project_metadata.contract_version,
    )


@router.get("/version")
def version():
    return project_metadata.model_dump()


@router.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    statuses = await verification_orchestrator.readiness()
    global_status = (
        "ready"
        if statuses["core"]["status"] == STATUS_READY
        and statuses["antispoof"]["status"] == STATUS_READY
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
    request_id, correlation_id = _resolve_request_identifiers(
        x_request_id=x_request_id,
        x_correlation_id=x_correlation_id,
    )

    try:
        validate_input_type(payload.input_type)
        result = await run_verification_use_case.execute(
            VerifyCommand(
                image_base64=payload.image_base64,
                request_id=request_id,
                correlation_id=correlation_id,
                majority_country=payload.majority_country,
                age_threshold=payload.age_threshold,
            )
        )

        return filter_verify_response(result)

    except UnsupportedInputTypeError as exc:
        verification_orchestrator.log_event(
            event="verification_rejected",
            request_id=request_id,
            correlation_id=correlation_id,
            extra_data={
                "error_type": LOG_ERROR_TYPE_VALIDATION,
                "error_code": "UNSUPPORTED_INPUT_TYPE",
            },
        )
        return _error_response(
            status_code=400,
            request_id=request_id,
            correlation_id=correlation_id,
            code="UNSUPPORTED_INPUT_TYPE",
            message=str(exc),
        )

    except ValueError:
        verification_orchestrator.log_event(
            event="verification_rejected",
            request_id=request_id,
            correlation_id=correlation_id,
            extra_data={
                "error_type": LOG_ERROR_TYPE_VALIDATION,
                "error_code": ERROR_INVALID_BASE64,
            },
        )
        return _error_response(
            status_code=400,
            request_id=request_id,
            correlation_id=correlation_id,
            code=ERROR_INVALID_BASE64,
            message="Invalid request.",
        )

    except Exception:
        verification_orchestrator.log_event(
            event="verification_failed",
            request_id=request_id,
            correlation_id=correlation_id,
            extra_data={
                "error_type": LOG_ERROR_TYPE_DOWNSTREAM,
                "error_code": ERROR_DOWNSTREAM,
            },
        )
        return _error_response(
            status_code=502,
            request_id=request_id,
            correlation_id=correlation_id,
            code=ERROR_DOWNSTREAM,
            message="An upstream service error has occurred.",
        )


async def handle_request_validation_error(
    request: Request,
    exc: RequestValidationError,
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

    verification_orchestrator.log_event(
        event="verification_rejected",
        request_id=request_id,
        correlation_id=correlation_id,
        extra_data={
            "error_type": LOG_ERROR_TYPE_VALIDATION,
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
            return ERROR_MISSING_IMAGE

    return ERROR_INVALID_REQUEST
