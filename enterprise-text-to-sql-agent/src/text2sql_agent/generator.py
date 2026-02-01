import re
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class GenerationResult:
    outcome_type: str
    sql: Optional[str]
    parameters: Dict[str, str]
    rationale: str
    clarification: Optional[str] = None
    time_window: Optional[str] = None


class LLMAdapter:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def generate(self, question: str, schema_dict: Dict[str, Dict[str, str]]) -> GenerationResult:
        if not self.enabled:
            return GenerationResult(
                outcome_type="SAFE_ERROR",
                sql=None,
                parameters={},
                rationale="LLM adapter disabled.",
                clarification=None,
            )
        raise NotImplementedError("LLM adapter not implemented in offline mode.")


class RuleBasedGenerator:
    def generate(self, question: str, schema_dict: Dict[str, Dict[str, str]]) -> GenerationResult:
        normalized = " ".join(question.lower().strip().split())
        if _contains_unsafe_keywords(normalized):
            return GenerationResult(
                outcome_type="SAFE_ERROR",
                sql=None,
                parameters={},
                rationale="Unsafe keywords detected in the request.",
                clarification=None,
            )
        time_filter_orders, params, time_note = _parse_time_filter(normalized, "order_date")
        time_filter_ship, _, _ = _parse_time_filter(normalized, "shipped_date")
        time_filter_delivery, _, _ = _parse_time_filter(normalized, "delivered_date")
        if _needs_time_filter(normalized) and not time_filter_orders:
            return GenerationResult(
                outcome_type="CLARIFY",
                sql=None,
                parameters={},
                rationale="KPI requires a time window to be meaningful.",
                clarification="Which time window should I use (e.g., last 30 days, this month)?",
            )

        if "order fill rate" in normalized:
            sql = (
                "SELECT "
                "ROUND(SUM(filled_qty) * 1.0 / NULLIF(SUM(ordered_qty), 0), 4) AS value, "
                "'ratio' AS unit "
                "FROM orders "
                f"{time_filter_orders}"
            )
            rationale = "Order fill rate is filled_qty / ordered_qty over the time window."
            return GenerationResult("SUCCESS", sql, params, rationale, time_window=time_note)

        if "late ship rate" in normalized or "late shipment rate" in normalized:
            sql = (
                "SELECT "
                "ROUND(SUM(CASE WHEN shipped_date > promised_date THEN 1 ELSE 0 END) * 1.0 "
                "/ NULLIF(COUNT(*), 0), 4) AS value, "
                "'ratio' AS unit "
                "FROM shipments "
                f"{time_filter_ship}"
            )
            rationale = "Late ship rate counts shipments after promised_date."
            return GenerationResult("SUCCESS", sql, params, rationale, time_window=time_note)

        if "on time delivery rate" in normalized or "on-time delivery rate" in normalized:
            sql = (
                "SELECT "
                "ROUND(SUM(CASE WHEN delivered_date <= promised_date THEN 1 ELSE 0 END) * 1.0 "
                "/ NULLIF(COUNT(*), 0), 4) AS value, "
                "'ratio' AS unit "
                "FROM shipments "
                f"{time_filter_delivery}"
            )
            rationale = "On-time delivery rate checks delivered_date <= promised_date."
            return GenerationResult("SUCCESS", sql, params, rationale, time_window=time_note)

        if "backlog units" in normalized or "backlog" in normalized:
            sql = (
                "SELECT SUM(ordered_qty - filled_qty) AS value, 'units' AS unit "
                "FROM orders WHERE status = 'BACKLOG'"
            )
            rationale = "Backlog units are remaining units on backlog orders."
            return GenerationResult("SUCCESS", sql, params, rationale, time_window=time_note)

        if "total revenue" in normalized or "revenue" in normalized:
            sql = (
                "SELECT ROUND(SUM(order_total), 2) AS value, 'usd' AS unit "
                "FROM orders "
                f"{time_filter_orders}"
            )
            rationale = "Total revenue sums order_total."
            return GenerationResult("SUCCESS", sql, params, rationale, time_window=time_note)

        if "orders count" in normalized or "number of orders" in normalized:
            sql = (
                "SELECT COUNT(*) AS value, 'count' AS unit FROM orders "
                f"{time_filter_orders}"
            )
            rationale = "Counts total orders."
            return GenerationResult("SUCCESS", sql, params, rationale)

        if "inventory units" in normalized or "inventory on hand" in normalized:
            sql = "SELECT SUM(on_hand_qty) AS value, 'units' AS unit FROM inventory"
            rationale = "Inventory units sum on_hand_qty."
            return GenerationResult("SUCCESS", sql, params, rationale)

        return GenerationResult(
            outcome_type="CLARIFY",
            sql=None,
            parameters={},
            rationale="Unable to map question to a known KPI template.",
            clarification="Which KPI are you asking about? Examples: order fill rate, late ship rate.",
        )


def _needs_time_filter(normalized: str) -> bool:
    return any(
        phrase in normalized
        for phrase in ["rate", "revenue", "orders count", "number of orders"]
    )


def _parse_time_filter(normalized: str, column: str) -> tuple[str, Dict[str, str], str]:
    params: Dict[str, str] = {}
    if "last 7 days" in normalized:
        return f"WHERE {column} >= date('now','-7 day')", params, "last 7 days"
    if "last 30 days" in normalized:
        return f"WHERE {column} >= date('now','-30 day')", params, "last 30 days"
    if "last month" in normalized:
        return (
            f"WHERE {column} >= date('now','start of month','-1 month') "
            f"AND {column} < date('now','start of month')",
            params,
            "last month",
        )
    if "this month" in normalized:
        return f"WHERE {column} >= date('now','start of month')", params, "this month"
    if "yesterday" in normalized:
        return f"WHERE {column} = date('now','-1 day')", params, "yesterday"
    if "today" in normalized:
        return f"WHERE {column} = date('now')", params, "today"
    return "", params, ""


def _contains_unsafe_keywords(normalized: str) -> bool:
    return bool(
        re.search(r"\b(drop|delete|update|insert|alter|pragma|attach|union)\b", normalized)
    )
