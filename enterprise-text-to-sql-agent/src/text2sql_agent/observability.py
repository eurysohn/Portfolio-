import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TraceContext:
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class JsonLogger:
    def __init__(self, log_path: str = "logs/trace.jsonl") -> None:
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log(self, payload: Dict[str, Any]) -> None:
        payload = dict(payload)
        payload.setdefault("timestamp", _utc_timestamp())
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")


class Observability:
    def __init__(self, logger: Optional[JsonLogger] = None) -> None:
        self.logger = logger or JsonLogger()

    def log_event(
        self,
        ctx: TraceContext,
        *,
        level: str,
        stage: str,
        message: str,
        cache_hit: Optional[bool] = None,
        validation_passed: Optional[bool] = None,
        outcome_type: Optional[str] = None,
        latency_ms: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload: Dict[str, Any] = {
            "level": level,
            "run_id": ctx.run_id,
            "trace_id": ctx.trace_id,
            "stage": stage,
            "message": message,
        }
        if cache_hit is not None:
            payload["cache_hit"] = cache_hit
        if validation_passed is not None:
            payload["validation_passed"] = validation_passed
        if outcome_type is not None:
            payload["outcome_type"] = outcome_type
        if latency_ms is not None:
            payload["latency_ms"] = latency_ms
        if extra:
            payload.update(extra)
        self.logger.log(payload)


class Timer:
    def __init__(self) -> None:
        self.start = time.perf_counter()

    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self.start) * 1000
