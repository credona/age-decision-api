from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.routes import handle_request_validation_error, router
from app.config.settings import settings
from app.logging_config import configure_logging
from app.project import project_metadata

configure_logging(settings.log_level)

app = FastAPI(
    title=project_metadata.app_name,
    version=project_metadata.version,
    description=settings.api_description,
)

app.add_exception_handler(RequestValidationError, handle_request_validation_error)

app.include_router(router)
