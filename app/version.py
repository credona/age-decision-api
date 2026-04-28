"""Application version metadata.

This module keeps backward-compatible constants while project metadata is now
loaded from project.json.
"""

from app.project import project_metadata

API_VERSION = project_metadata.version
APP_NAME = project_metadata.app_name
SERVICE_NAME = project_metadata.service_name
CONTRACT_VERSION = project_metadata.contract_version
