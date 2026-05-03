import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.domain.privacy.safe_logging import sanitize_log_payload
from app.project import project_metadata


class JsonFormatter(logging.Formatter):
    """Privacy-safe JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        base_payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname.lower(),
            "service": project_metadata.service_name,
            "version": project_metadata.version,
            "contract_version": project_metadata.contract_version,
            "logger": record.name,
        }

        event_payload = {
            "event": getattr(record, "event", record.getMessage()),
            "request_id": getattr(record, "request_id", None),
            "correlation_id": getattr(record, "correlation_id", None),
        }

        extra_data = getattr(record, "extra_data", {})
        if isinstance(extra_data, dict):
            event_payload.update(extra_data)

        safe_payload = sanitize_log_payload(event_payload)

        return json.dumps(
            {
                **base_payload,
                **safe_payload,
            },
            default=str,
            ensure_ascii=False,
            sort_keys=True,
        )


def configure_logging(log_level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())
