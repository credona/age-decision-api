import json
import logging
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    """
    JSON log formatter compatible with ELK, Datadog and most log pipelines.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event"):
            payload["event"] = record.event

        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id

        if hasattr(record, "correlation_id"):
            payload["correlation_id"] = record.correlation_id

        if hasattr(record, "extra_data"):
            payload["data"] = record.extra_data

        return json.dumps(payload, default=str)


def configure_logging(log_level: str) -> None:
    """
    Configure application logging once at startup.
    """

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())