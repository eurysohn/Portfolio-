"""Mock HTTP tool."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "mock_http.json"


def _load_routes() -> dict[str, Any]:
    with open(DATA_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def http_request(args: dict[str, Any]) -> dict[str, Any]:
    method = str(args.get("method", "GET")).upper()
    path = str(args.get("path", "/health"))
    routes = _load_routes().get("routes", {})
    response = routes.get(path, routes.get("default", {}))
    latency_ms = random.randint(20, 120)
    return {
        "method": method,
        "path": path,
        "status": response.get("status", 404),
        "latency_ms": latency_ms,
        "body": response.get("body", {"message": "Not found"}),
    }
