"""Runbook agent workflow."""

from __future__ import annotations

from runtime.models import AgentPlan, ToolCall


def build_plan(ticket: str) -> AgentPlan:
    return AgentPlan(
        classification="runbook_request",
        tool_calls=[
            ToolCall(
                name="runbook_lookup",
                args={"query": ticket},
            )
        ],
        action_plan=[
            "Search runbook for relevant remediation steps.",
            "Summarize key steps for the operator.",
        ],
    )
