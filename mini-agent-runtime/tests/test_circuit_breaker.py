from runtime.executor import ToolExecutor
from runtime.models import Tool, ToolCall
from runtime.tooling import ToolRegistry


def test_circuit_breaker_opens_after_failures():
    def always_fail(_args):
        raise RuntimeError("boom")

    registry = ToolRegistry()
    registry.register(Tool(name="fail", input_schema={"type": "object"}, invoke=always_fail))
    executor = ToolExecutor(registry)

    for _ in range(4):
        executor.execute(ToolCall(name="fail", args={}))

    result = executor.execute(ToolCall(name="fail", args={}))
    assert result.ok is False
    assert result.error == "circuit_breaker_open"
