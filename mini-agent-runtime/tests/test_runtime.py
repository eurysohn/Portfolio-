from runtime.engine import AgentRuntime


def test_runtime_runbook_flow():
    runtime = AgentRuntime()
    result = runtime.run("How do I restart the payments service?")
    assert result.route == "runbook_lookup"
    assert result.tool_calls[0].name == "runbook_lookup"


def test_runtime_escalation_low_signal():
    runtime = AgentRuntime()
    result = runtime.run("Hello there")
    assert result.escalate is True
