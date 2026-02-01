from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from sqlalchemy import create_engine, text


@dataclass
class ExecutionResult:
    rows: List[Dict[str, Any]]
    row_count: int


class SQLExecutor:
    def __init__(self, db_url: str) -> None:
        self.db_url = db_url

    def run(self, sql: str, parameters: Dict[str, Any]) -> ExecutionResult:
        engine = create_engine(self.db_url)
        with engine.connect() as connection:
            result = connection.execute(text(sql), parameters)
            rows = [dict(row._mapping) for row in result]
        return ExecutionResult(rows=rows, row_count=len(rows))


def summarize_kpi(rows: List[Dict[str, Any]], time_window: Optional[str]) -> Dict[str, Any]:
    if not rows:
        return {
            "value": 0,
            "unit": "count",
            "summary": "No data available for the specified time period.",
            "time_window": time_window,
        }
    first = rows[0]
    value = first.get("value")
    unit = first.get("unit", "")
    
    # Handle None values
    if value is None:
        value = 0
    
    # Format value nicely
    if isinstance(value, float):
        if unit == "ratio":
            # Show as percentage for ratios
            formatted_value = f"{value * 100:.2f}%"
        elif unit == "usd":
            formatted_value = f"${value:,.2f}"
        else:
            formatted_value = f"{value:.2f}"
    else:
        formatted_value = f"{value:,}"
    
    # Build summary with proper formatting
    if time_window:
        summary = f"**{formatted_value}** ({time_window})"
    else:
        summary = f"**{formatted_value}**"
    
    return {
        "value": value,
        "unit": unit,
        "summary": summary,
        "time_window": time_window,
    }
