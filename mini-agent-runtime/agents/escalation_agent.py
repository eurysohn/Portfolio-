"""Escalation workflow."""

from __future__ import annotations

from runtime.models import AgentPlan, ToolCall


def build_plan(ticket: str) -> AgentPlan:
    return AgentPlan(
        classification="escalation",
        tool_calls=[
            ToolCall(
                name="notify_oncall",
                args={"ticket": ticket},
            )
        ],
        action_plan=[
            "Notify on-call engineer with summary.",
            "Provide initial triage notes and context.",
        ],
    )
