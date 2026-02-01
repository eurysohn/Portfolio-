"""Core agent runtime engine."""

from __future__ import annotations

import json
import uuid
from typing import Iterable

from agents.data_query_agent import build_plan as data_query_plan
from agents.escalation_agent import build_plan as escalation_plan
from agents.runbook_agent import build_plan as runbook_plan
from observability.logging import get_logger, set_context
from observability.tracing import TraceEvent, now_ts, trace_store
from runtime.executor import ToolExecutor
from runtime.models import AgentResult, ToolCall, ToolResult
from runtime.router import decide_route
from runtime.security import guardrails_check, redact_pii
from tools.registry import build_registry


class AgentRuntime:
    def __init__(self) -> None:
        self.registry = build_registry()
        self.executor = ToolExecutor(self.registry)
        self.logger = get_logger("runtime")

    def run(self, ticket: str, correlation_id: str | None = None) -> AgentResult:
        run_id = uuid.uuid4().hex
        trace_id = uuid.uuid4().hex
        correlation_id = correlation_id or uuid.uuid4().hex
        set_context(correlation_id, trace_id, run_id)

        redacted_ticket = redact_pii(ticket)
        guardrail = guardrails_check(redacted_ticket)
        if guardrail.blocked:
            route = "escalate"
            confidence = 0.1
            reason = guardrail.reason or "guardrail_block"
        else:
            decision = decide_route(redacted_ticket)
            route = decision.route
            confidence = decision.confidence
            reason = decision.reason

        self._trace(
            run_id,
            trace_id,
            correlation_id,
            "run_start",
            "Agent run started",
            {"ticket": redacted_ticket},
        )

        self._trace(
            run_id,
            trace_id,
            correlation_id,
            "route_decision",
            "Routing decision",
            {"route": route, "confidence": confidence, "reason": reason},
        )

        plan, tool_calls = self._select_plan(route, redacted_ticket)
        tool_results = self._execute_tools(run_id, trace_id, correlation_id, tool_calls)

        escalate = route == "escalate" or confidence < 0.45
        escalation_reason = None
        if guardrail.blocked:
            escalation_reason = guardrail.reason
        elif confidence < 0.45:
            escalation_reason = "low_confidence"

        self._trace(
            run_id,
            trace_id,
            correlation_id,
            "run_complete",
            "Agent run complete",
            {
                "route": route,
                "confidence": confidence,
                "tool_results_ok": [result.ok for result in tool_results],
                "escalate": escalate,
            },
        )

        self.logger.info(
            json.dumps(
                {
                    "event": "run_complete",
                    "route": route,
                    "confidence": confidence,
                    "escalate": escalate,
                }
            )
        )

        return AgentResult(
            run_id=run_id,
            trace_id=trace_id,
            correlation_id=correlation_id,
            redacted_ticket=redacted_ticket,
            classification=plan.classification,
            route=route,
            confidence=confidence,
            tool_calls=tool_calls,
            tool_results=tool_results,
            action_plan=plan.action_plan,
            escalate=escalate,
            escalation_reason=escalation_reason,
        )

    def _select_plan(self, route: str, ticket: str):
        if route == "runbook_lookup":
            plan = runbook_plan(ticket)
        elif route == "data_query":
            plan = data_query_plan(ticket)
        else:
            plan = escalation_plan(ticket)
        return plan, plan.tool_calls

    def _execute_tools(
        self,
        run_id: str,
        trace_id: str,
        correlation_id: str,
        calls: Iterable[ToolCall],
    ) -> list[ToolResult]:
        results = []
        for call in calls:
            self._trace(
                run_id=run_id,
                trace_id=trace_id,
                correlation_id=correlation_id,
                event_type="tool_call",
                message=f"Invoking tool {call.name}",
                data={"args": call.args},
            )
            result = self.executor.execute(call)
            self._trace(
                run_id=run_id,
                trace_id=trace_id,
                correlation_id=correlation_id,
                event_type="tool_result",
                message=f"Tool {call.name} completed",
                data={"ok": result.ok, "error": result.error},
            )
            results.append(result)
        return results

    def _trace(
        self,
        run_id: str,
        trace_id: str,
        correlation_id: str,
        event_type: str,
        message: str,
        data: dict,
    ) -> None:
        trace_store.record(
            TraceEvent(
                run_id=run_id,
                trace_id=trace_id,
                correlation_id=correlation_id,
                event_type=event_type,
                message=message,
                data=data,
                timestamp=now_ts(),
            )
        )
