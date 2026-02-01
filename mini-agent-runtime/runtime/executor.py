"""Tool execution with retries, timeouts, and circuit breaker support."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any

from runtime import config
from runtime.models import ToolCall, ToolResult
from runtime.tooling import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, call: ToolCall) -> ToolResult:
        tool = self.registry.get(call.name)
        breaker = self.registry.breaker_for(call.name)
        if not breaker.allow():
            return ToolResult(
                name=call.name,
                ok=False,
                output=None,
                error="circuit_breaker_open",
                latency_ms=0.0,
                attempts=0,
            )

        attempts = 0
        start = time.time()
        last_error: str | None = None
        while attempts <= config.TOOL_MAX_RETRIES:
            attempts += 1
            try:
                pool = ThreadPoolExecutor(max_workers=1)
                future = pool.submit(tool.invoke, call.args)
                output: dict[str, Any] = future.result(timeout=config.TOOL_TIMEOUT_S)
                pool.shutdown(wait=False, cancel_futures=True)
                breaker.record_success()
                latency_ms = (time.time() - start) * 1000
                return ToolResult(
                    name=call.name,
                    ok=True,
                    output=output,
                    error=None,
                    latency_ms=latency_ms,
                    attempts=attempts,
                )
            except TimeoutError:
                future.cancel()
                pool.shutdown(wait=False, cancel_futures=True)
                last_error = "timeout"
                breaker.record_failure()
            except Exception as exc:  # noqa: BLE001
                pool.shutdown(wait=False, cancel_futures=True)
                last_error = f"error:{exc}"
                breaker.record_failure()
            if attempts <= config.TOOL_MAX_RETRIES:
                time.sleep(config.TOOL_BACKOFF_BASE_S * (2 ** (attempts - 1)))
        latency_ms = (time.time() - start) * 1000
        return ToolResult(
            name=call.name,
            ok=False,
            output=None,
            error=last_error,
            latency_ms=latency_ms,
            attempts=attempts,
        )
