"""Data query agent workflow."""

from __future__ import annotations

from runtime.models import AgentPlan, ToolCall


def build_plan(ticket: str) -> AgentPlan:
    lowered = ticket.lower()
    tool_calls = [
        ToolCall(
            name="data_query",
            args={"query": ticket},
        )
    ]
    if any(keyword in lowered for keyword in {"api", "endpoint", "http"}):
        tool_calls.append(
            ToolCall(
                name="http_request",
                args={"method": "GET", "path": "/health"},
            )
        )
    if any(keyword in lowered for keyword in {"db", "database", "sql", "query"}):
        tool_calls.append(
            ToolCall(
                name="db_query",
                args={"table": "incidents", "filters": {"status": "open"}},
            )
        )
    return AgentPlan(
        classification="data_query",
        tool_calls=tool_calls,
        action_plan=[
            "Run diagnostics query to gather operational data.",
            "Check mocked API or DB signals if referenced.",
            "Summarize anomalies and recommended next steps.",
        ],
    )
