import time

from runtime import config
from runtime.executor import ToolExecutor
from runtime.models import Tool, ToolCall
from runtime.tooling import ToolRegistry


def test_tool_executor_success():
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="echo",
            input_schema={"type": "object"},
            invoke=lambda args: {"ok": True, "input": args},
        )
    )
    executor = ToolExecutor(registry)
    result = executor.execute(ToolCall(name="echo", args={"foo": "bar"}))
    assert result.ok is True
    assert result.output["input"]["foo"] == "bar"


def test_tool_executor_timeout():
    prev_timeout = config.TOOL_TIMEOUT_S
    prev_retries = config.TOOL_MAX_RETRIES
    config.TOOL_TIMEOUT_S = 0.1
    config.TOOL_MAX_RETRIES = 0

    def slow(_args):
        time.sleep(5)
        return {"ok": True}

    registry = ToolRegistry()
    registry.register(Tool(name="slow", input_schema={"type": "object"}, invoke=slow))
    executor = ToolExecutor(registry)
    try:
        result = executor.execute(ToolCall(name="slow", args={}))
        assert result.ok is False
        assert result.error == "timeout"
    finally:
        config.TOOL_TIMEOUT_S = prev_timeout
        config.TOOL_MAX_RETRIES = prev_retries


def test_tool_executor_retry_then_success():
    prev_retries = config.TOOL_MAX_RETRIES
    prev_backoff = config.TOOL_BACKOFF_BASE_S
    config.TOOL_MAX_RETRIES = 2
    config.TOOL_BACKOFF_BASE_S = 0.0
    attempts = {"count": 0}

    def flaky(_args):
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise RuntimeError("fail once")
        return {"ok": True}

    registry = ToolRegistry()
    registry.register(Tool(name="flaky", input_schema={"type": "object"}, invoke=flaky))
    executor = ToolExecutor(registry)
    try:
        result = executor.execute(ToolCall(name="flaky", args={}))
        assert result.ok is True
        assert result.attempts >= 2
    finally:
        config.TOOL_MAX_RETRIES = prev_retries
        config.TOOL_BACKOFF_BASE_S = prev_backoff
