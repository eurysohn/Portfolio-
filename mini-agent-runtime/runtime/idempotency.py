"""Idempotency store for agent runs."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any

from runtime.config import IDEMPOTENCY_TTL_S


@dataclass
class IdempotencyRecord:
    value: Any
    created_at: float


class IdempotencyStore:
    def __init__(self, ttl_s: float = IDEMPOTENCY_TTL_S) -> None:
        self.ttl_s = ttl_s
        self._records: dict[str, IdempotencyRecord] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            record = self._records.get(key)
            if not record:
                return None
            if (time.time() - record.created_at) > self.ttl_s:
                self._records.pop(key, None)
                return None
            return record.value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._records[key] = IdempotencyRecord(value=value, created_at=time.time())


idempotency_store = IdempotencyStore()
