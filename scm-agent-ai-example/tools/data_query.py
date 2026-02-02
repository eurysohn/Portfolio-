import json
from pathlib import Path
from typing import Dict, Optional

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "structured_kpis.json"


def query_kpi(query: str) -> Optional[Dict]:
    if not DATA_PATH.exists():
        return None
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    q = query.lower()
    if "latest month" in q or "last month" in q:
        return {"type": "latest_month", "data": payload.get("latest_month", {})}
    if "latest week" in q or "last week" in q:
        return {"type": "latest_week", "data": payload.get("latest_week", {})}
    return None
