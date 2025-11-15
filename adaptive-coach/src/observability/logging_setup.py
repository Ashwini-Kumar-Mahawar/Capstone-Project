# src/observability/logging_setup.py
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # ISO 8601 with timezone naive (for demo). Replace with timezone-aware in prod.
        return datetime.utcfromtimestamp(record.created).isoformat() + "Z"

    def format(self, record):
        base = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        # include any structured data passed in record.__dict__ under 'extra'
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            base.update(extra)
        # include exception info if present
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)

def get_logger(name="adaptive_coach"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
