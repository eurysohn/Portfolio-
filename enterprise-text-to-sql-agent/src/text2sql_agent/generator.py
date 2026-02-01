import re
from dataclasses import dataclass
from typing import Dict, Optional, Union


@dataclass
class GenerationResult:
    outcome_type: str
    sql: Optional[str]
    parameters: Dict[str, str]
    rationale: str
    clarification: Optional[str] = None
    time_window: Optional[str] = None


class LLMAdapter:
    """LLM-powered SQL generator using OpenAI with prompt engineering."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", temperature: float = 0.0) -> None:
        self.enabled = api_key is not None
        self.model = model
        self.temperature = temperature
        if self.enabled:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)

    def generate(self, question: str, schema_dict: Dict[str, Dict[str, str]]) -> GenerationResult:
        if not self.enabled:
            return GenerationResult(
                outcome_type="SAFE_ERROR",
                sql=None,
                parameters={},
                rationale="LLM adapter is not enabled. Set OPENAI_API_KEY in .env file.",
                clarification=None,
            )

        try:
            # Build system prompt with schema context
            system_prompt = self._build_system_prompt(schema_dict)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Extract time window if present
            time_window = self._extract_time_window(question)
            
            return GenerationResult(
                outcome_type=result.get("outcome_type", "SUCCESS"),
                sql=result.get("sql"),
                parameters={},
                rationale=result.get("rationale", ""),
                clarification=result.get("clarification"),
                time_window=time_window,
            )
        
        except Exception as e:
            return GenerationResult(
                outcome_type="SAFE_ERROR",
                sql=None,
                parameters={},
                rationale=f"LLM generation failed: {str(e)}",
                clarification=None,
            )

    def _build_system_prompt(self, schema_dict: Dict[str, Dict[str, str]]) -> str:
        """Build system prompt with schema and few-shot examples."""
        
        # Format schema information
        schema_lines = ["Available tables and columns:"]
        for table, columns in schema_dict.items():
            cols = ", ".join(columns.keys())
            schema_lines.append(f"- {table}: {cols}")
        schema_str = "\n".join(schema_lines)
        
        return f"""You are an enterprise SQL agent that generates safe, read-only SQL queries for KPI questions.

{schema_str}

RULES:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP)
2. Only use tables and columns from the schema above
3. Use SQLite syntax and functions (like date('now','-30 day'))
4. Return results with 'value' and 'unit' columns
5. If the question is not a KPI question, set outcome_type to "SAFE_ERROR"
6. If the question is ambiguous (e.g., missing time window), set outcome_type to "CLARIFY"

SUPPORTED KPIs:
- Order fill rate: SUM(filled_qty) / SUM(ordered_qty) from orders
- Late ship rate: count of shipments where shipped_date > promised_date
- On-time delivery rate: count where delivered_date <= promised_date
- Total revenue: SUM(order_total) from orders
- Orders count: COUNT(*) from orders
- Backlog units: SUM(ordered_qty - filled_qty) where status='BACKLOG'
- Inventory units: SUM(on_hand_qty) from inventory

FEW-SHOT EXAMPLES:

Q: "order fill rate last 30 days"
A: {{"outcome_type": "SUCCESS", "sql": "SELECT ROUND(SUM(filled_qty) * 1.0 / NULLIF(SUM(ordered_qty), 0), 4) AS value, 'ratio' AS unit FROM orders WHERE order_date >= date('now','-30 day')", "rationale": "Order fill rate is filled_qty / ordered_qty over the time window."}}

Q: "total revenue this month"
A: {{"outcome_type": "SUCCESS", "sql": "SELECT ROUND(SUM(order_total), 2) AS value, 'usd' AS unit FROM orders WHERE order_date >= date('now','start of month')", "rationale": "Total revenue sums order_total."}}

Q: "order fill rate"
A: {{"outcome_type": "CLARIFY", "sql": null, "rationale": "KPI requires a time window to be meaningful.", "clarification": "Which time window should I use (e.g., last 30 days, this month)?"}}

Q: "what is the weather?"
A: {{"outcome_type": "SAFE_ERROR", "sql": null, "rationale": "This agent only answers KPI questions. Examples: order fill rate, late ship rate, on-time delivery rate.", "clarification": null}}

OUTPUT FORMAT:
Return a JSON object with these fields:
- outcome_type: "SUCCESS", "CLARIFY", or "SAFE_ERROR"
- sql: the SQL query (or null)
- rationale: explanation of the calculation
- clarification: question to ask user (or null)
"""

    def _extract_time_window(self, question: str) -> Optional[str]:
        """Extract time window phrase from question."""
        normalized = question.lower()
        for phrase in ["last 7 days", "last 30 days", "last month", "this month", "yesterday", "today"]:
            if phrase in normalized:
                return phrase
        return None



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
            outcome_type="SAFE_ERROR",
            sql=None,
            parameters={},
            rationale=(
                "This agent only answers KPI questions. "
                "Examples: order fill rate, late ship rate, on-time delivery rate."
            ),
            clarification=None,
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
