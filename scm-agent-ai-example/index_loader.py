import os
from pathlib import Path
from typing import Dict

import boto3

from config import INDEX_CACHE_DIR


def _s3_client():
    region = os.getenv("AWS_REGION", "").strip() or None
    return boto3.client("s3", region_name=region)


def _download_if_missing(bucket: str, key: str, dest: Path) -> bool:
    if dest.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    _s3_client().download_file(bucket, key, str(dest))
    return True


def ensure_indexes() -> Dict[str, str]:
    bucket = os.getenv("INDEX_BUCKET", "").strip()
    if not bucket:
        return {"status": "skipped", "reason": "INDEX_BUCKET not set"}

    prefix = os.getenv("INDEX_PREFIX", "scm-agent-ai-example/indexes").strip().strip("/")
    supply_key = os.getenv(
        "INDEX_SUPPLY_KEY", f"{prefix}/vector_db_supply/index.pkl"
    ).strip()
    demand_key = os.getenv(
        "INDEX_DEMAND_KEY", f"{prefix}/vector_db_demand/index.pkl"
    ).strip()

    supply_dest = INDEX_CACHE_DIR / "vector_db_supply" / "index.pkl"
    demand_dest = INDEX_CACHE_DIR / "vector_db_demand" / "index.pkl"

    results = {
        "supply": "cached" if supply_dest.exists() else "downloaded",
        "demand": "cached" if demand_dest.exists() else "downloaded",
    }

    if results["supply"] == "downloaded":
        _download_if_missing(bucket, supply_key, supply_dest)
    if results["demand"] == "downloaded":
        _download_if_missing(bucket, demand_key, demand_dest)

    return results
