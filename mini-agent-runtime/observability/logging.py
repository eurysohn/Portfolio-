"""Structured JSON logging with correlation metadata."""

from __future__ import annotations

import json
import logging
import time
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="unknown")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="unknown")
run_id_var: ContextVar[str] = ContextVar("run_id", default="unknown")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": correlation_id_var.get(),
            "trace_id": trace_id_var.get(),
            "run_id": run_id_var.get(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"))


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(handler)
    root.setLevel(logging.INFO)


def set_context(correlation_id: str, trace_id: str, run_id: str) -> None:
    correlation_id_var.set(correlation_id)
    trace_id_var.set(trace_id)
    run_id_var.set(run_id)


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
