"""Runtime configuration defaults."""

from __future__ import annotations

import os

TRACE_JSONL_PATH = os.getenv("TRACE_JSONL_PATH", "logs/traces.jsonl")

TOOL_TIMEOUT_S = float(os.getenv("TOOL_TIMEOUT_S", "3.0"))
TOOL_MAX_RETRIES = int(os.getenv("TOOL_MAX_RETRIES", "2"))
TOOL_BACKOFF_BASE_S = float(os.getenv("TOOL_BACKOFF_BASE_S", "0.2"))

CB_FAILURE_THRESHOLD = int(os.getenv("CB_FAILURE_THRESHOLD", "3"))
CB_RESET_SECONDS = float(os.getenv("CB_RESET_SECONDS", "10"))
