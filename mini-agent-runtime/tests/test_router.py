from runtime.router import decide_route


def test_route_runbook():
    decision = decide_route("Need steps to restart service")
    assert decision.route == "runbook_lookup"
    assert decision.confidence >= 0.5


def test_route_data_query():
    decision = decide_route("Timeout errors and latency spike")
    assert decision.route == "data_query"
    assert decision.confidence >= 0.5


def test_route_escalate():
    decision = decide_route("Security breach incident")
    assert decision.route == "escalate"
    assert decision.confidence >= 0.8
