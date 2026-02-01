"""Rule-based judge for offline evaluation."""

from __future__ import annotations

from typing import Any


def judge_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expected_route = case["expected_route"]
    expected_escalate = case["expected_escalate"]
    route_match = result["route"] == expected_route
    escalate_match = result["escalate"] == expected_escalate
    tool_success = all(tool["ok"] for tool in result["tool_results"])
    passed = route_match and escalate_match
    return {
        "passed": passed,
        "route_match": route_match,
        "escalate_match": escalate_match,
        "tool_success": tool_success,
    }
