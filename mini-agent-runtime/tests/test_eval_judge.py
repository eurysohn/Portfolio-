from eval.judge import judge_case


def test_judge_case_pass():
    case = {"expected_route": "runbook_lookup", "expected_escalate": False}
    result = {
        "route": "runbook_lookup",
        "escalate": False,
        "tool_results": [{"ok": True}],
    }
    verdict = judge_case(case, result)
    assert verdict["passed"] is True
    assert verdict["tool_success"] is True
