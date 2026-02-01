"""In-memory trace store with optional JSONL persistence."""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from typing import Any

from runtime.config import TRACE_JSONL_PATH


@dataclass
class TraceEvent:
    run_id: str
    trace_id: str
    correlation_id: str
    event_type: str
    message: str
    data: dict[str, Any]
    timestamp: float


class TraceStore:
    def __init__(self, jsonl_path: str | None = None) -> None:
        self._events: dict[str, list[TraceEvent]] = {}
        self._lock = threading.Lock()
        self._jsonl_path = jsonl_path

    def record(self, event: TraceEvent) -> None:
        with self._lock:
            self._events.setdefault(event.run_id, []).append(event)
        if self._jsonl_path:
            self._persist(event)

    def _persist(self, event: TraceEvent) -> None:
        os.makedirs(os.path.dirname(self._jsonl_path), exist_ok=True)
        with open(self._jsonl_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), separators=(",", ":")) + "\n")

    def get_run(self, run_id: str) -> list[TraceEvent]:
        with self._lock:
            return list(self._events.get(run_id, []))

    def load_from_jsonl(self, run_id: str) -> list[TraceEvent]:
        if not self._jsonl_path or not os.path.exists(self._jsonl_path):
            return []
        events: list[TraceEvent] = []
        with open(self._jsonl_path, "r", encoding="utf-8") as handle:
            for line in handle:
                data = json.loads(line)
                if data.get("run_id") == run_id:
                    events.append(
                        TraceEvent(
                            run_id=data["run_id"],
                            trace_id=data["trace_id"],
                            correlation_id=data["correlation_id"],
                            event_type=data["event_type"],
                            message=data["message"],
                            data=data["data"],
                            timestamp=data["timestamp"],
                        )
                    )
        return events


def now_ts() -> float:
    return time.time()


trace_store = TraceStore(jsonl_path=TRACE_JSONL_PATH)
