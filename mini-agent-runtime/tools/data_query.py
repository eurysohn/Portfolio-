"""Mock data query tool."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "mock_data.json"


def _load_data() -> dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def data_query(args: dict[str, Any]) -> dict[str, Any]:
    query = str(args.get("query", "")).lower()
    data = _load_data()
    if "latency" in query or "timeout" in query:
        return {"metric": "p95_latency_ms", "value": data["metrics"]["p95_latency_ms"]}
    if "error" in query:
        return {"metric": "error_rate", "value": data["metrics"]["error_rate"]}
    if "usage" in query or "quota" in query:
        return {"metric": "daily_usage", "value": data["metrics"]["daily_usage"]}
    return {"note": "No matching metric found", "available": list(data["metrics"].keys())}
