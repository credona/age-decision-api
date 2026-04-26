from fastapi import FastAPI

from app.api.routes import router
from app.config.settings import settings
from app.logging_config import configure_logging

configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description=settings.api_description,
)

app.include_router(router)