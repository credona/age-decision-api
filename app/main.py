from fastapi import FastAPI

from app.api.routes import router
from app.config.settings import settings
from app.logging_config import configure_logging
from app.project import project_metadata

configure_logging(settings.log_level)

app = FastAPI(
    title=project_metadata.app_name,
    version=project_metadata.version,
    description=settings.api_description,
)

app.include_router(router)
