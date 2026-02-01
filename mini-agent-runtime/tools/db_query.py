"""Mock DB query tool."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "mock_db.json"


def _load_db() -> dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _matches_filters(row: dict[str, Any], filters: dict[str, Any]) -> bool:
    for key, value in filters.items():
        if row.get(key) != value:
            return False
    return True


def db_query(args: dict[str, Any]) -> dict[str, Any]:
    table = str(args.get("table", "incidents"))
    filters = args.get("filters") or {}
    db = _load_db()
    rows = db.get("tables", {}).get(table, [])
    results = [row for row in rows if _matches_filters(row, filters)]
    return {"table": table, "filters": filters, "rows": results, "count": len(results)}
