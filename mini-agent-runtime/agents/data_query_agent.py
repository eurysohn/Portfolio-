"""Data query agent workflow."""

from __future__ import annotations

from runtime.models import AgentPlan, ToolCall


def build_plan(ticket: str) -> AgentPlan:
    return AgentPlan(
        classification="data_query",
        tool_calls=[
            ToolCall(
                name="data_query",
                args={"query": ticket},
            )
        ],
        action_plan=[
            "Run diagnostics query to gather operational data.",
            "Summarize anomalies and recommended next steps.",
        ],
    )
