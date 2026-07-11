import logging
import logging.config
import os
from pathlib import Path

from backend.app.core.config import settings


def configure_logging() -> None:
    log_file = Path(os.getenv("LOG_FILE", "backend/logs/app.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": settings.log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": os.getenv("LOG_FILE", "backend/logs/app.log"),
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 3,
                    "formatter": "default",
                },
            },
            "root": {"handlers": ["console", "file"], "level": log_level},
        }
    )
