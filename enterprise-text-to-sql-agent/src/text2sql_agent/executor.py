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


def summarize_kpi(rows: List[Dict[str, Any]], time_window: str | None) -> Dict[str, Any]:
    if not rows:
        return {
            "value": None,
            "unit": None,
            "summary": "No results found.",
            "time_window": time_window,
        }
    first = rows[0]
    value = first.get("value")
    unit = first.get("unit")
    summary = f"KPI value: {value} {unit}".strip()
    return {
        "value": value,
        "unit": unit,
        "summary": summary,
        "time_window": time_window,
    }
