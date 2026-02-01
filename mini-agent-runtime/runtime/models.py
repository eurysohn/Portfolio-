"""Shared runtime data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class RouteDecision:
    route: str
    confidence: float
    reason: str


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class ToolResult:
    name: str
    ok: bool
    output: dict[str, Any] | None
    error: str | None
    latency_ms: float
    attempts: int


@dataclass
class Tool:
    name: str
    input_schema: dict[str, Any]
    invoke: Callable[[dict[str, Any]], dict[str, Any]]
    description: str = ""


@dataclass
class AgentPlan:
    tool_calls: list[ToolCall] = field(default_factory=list)
    action_plan: list[str] = field(default_factory=list)
    classification: str = ""


@dataclass
class AgentResult:
    run_id: str
    trace_id: str
    correlation_id: str
    redacted_ticket: str
    classification: str
    route: str
    confidence: float
    tool_calls: list[ToolCall]
    tool_results: list[ToolResult]
    action_plan: list[str]
    escalate: bool
    escalation_reason: str | None
