"""Runbook lookup tool."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "runbooks.json"


def _load_runbooks() -> list[dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def runbook_lookup(args: dict[str, Any]) -> dict[str, Any]:
    query = str(args.get("query", "")).lower()
    runbooks = _load_runbooks()
    best = None
    best_score = 0
    for runbook in runbooks:
        score = sum(1 for keyword in runbook["keywords"] if keyword in query)
        if score > best_score:
            best_score = score
            best = runbook
    if not best:
        return {"found": False, "summary": "No matching runbook found."}
    return {
        "found": True,
        "title": best["title"],
        "steps": best["steps"],
    }
