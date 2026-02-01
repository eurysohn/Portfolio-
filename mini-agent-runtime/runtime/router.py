"""Rule-based router for ticket workflows."""

from __future__ import annotations

from runtime.models import RouteDecision


RUNBOOK_KEYWORDS = {"how", "procedure", "steps", "runbook", "guide", "restart", "reset"}
DATA_KEYWORDS = {"latency", "error", "timeout", "metrics", "usage", "report", "db", "query"}
ESCALATE_KEYWORDS = {"breach", "security", "urgent", "sev1", "sev0", "incident"}


def decide_route(ticket: str) -> RouteDecision:
    lowered = ticket.lower()
    runbook_score = sum(1 for word in RUNBOOK_KEYWORDS if word in lowered)
    data_score = sum(1 for word in DATA_KEYWORDS if word in lowered)
    escalate_score = sum(1 for word in ESCALATE_KEYWORDS if word in lowered)

    if escalate_score > 0:
        return RouteDecision(route="escalate", confidence=0.9, reason="escalation_keyword")
    if runbook_score > data_score:
        confidence = min(0.9, 0.5 + runbook_score * 0.1)
        return RouteDecision(route="runbook_lookup", confidence=confidence, reason="runbook_keywords")
    if data_score > 0:
        confidence = min(0.9, 0.5 + data_score * 0.1)
        return RouteDecision(route="data_query", confidence=confidence, reason="data_keywords")
    return RouteDecision(route="escalate", confidence=0.3, reason="low_signal")
