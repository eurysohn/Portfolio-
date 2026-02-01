"""Tool registry and circuit breaker management."""

from __future__ import annotations

import time
from dataclasses import dataclass

from runtime.config import CB_FAILURE_THRESHOLD, CB_RESET_SECONDS
from runtime.models import Tool


@dataclass
class CircuitBreakerState:
    status: str = "closed"
    failure_count: int = 0
    opened_at: float | None = None


class CircuitBreaker:
    def __init__(self, threshold: int = CB_FAILURE_THRESHOLD, reset_s: float = CB_RESET_SECONDS) -> None:
        self.threshold = threshold
        self.reset_s = reset_s
        self.state = CircuitBreakerState()

    def allow(self) -> bool:
        if self.state.status == "closed":
            return True
        if self.state.status == "open":
            if self.state.opened_at and (time.time() - self.state.opened_at) > self.reset_s:
                self.state.status = "half-open"
                return True
            return False
        return True

    def record_success(self) -> None:
        self.state.status = "closed"
        self.state.failure_count = 0
        self.state.opened_at = None

    def record_failure(self) -> None:
        self.state.failure_count += 1
        if self.state.failure_count >= self.threshold:
            self.state.status = "open"
            self.state.opened_at = time.time()


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._breakers: dict[str, CircuitBreaker] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool
        self._breakers.setdefault(tool.name, CircuitBreaker())

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def breaker_for(self, name: str) -> CircuitBreaker:
        return self._breakers.setdefault(name, CircuitBreaker())
