import os
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent


def _path_env(name: str, default: Path) -> Path:
    value = os.getenv(name, "").strip()
    return Path(value) if value else default


INDEX_CACHE_DIR = _path_env("INDEX_CACHE_DIR", BASE_DIR / "cache")


def get_index_path(domain: Optional[str] = None) -> Path:
    if domain == "supply":
        cache_path = INDEX_CACHE_DIR / "vector_db_supply" / "index.pkl"
        default_path = BASE_DIR / "storage" / "vector_db_supply" / "index.pkl"
    elif domain == "demand":
        cache_path = INDEX_CACHE_DIR / "vector_db_demand" / "index.pkl"
        default_path = BASE_DIR / "storage" / "vector_db_demand" / "index.pkl"
    else:
        cache_path = INDEX_CACHE_DIR / "vector_db" / "index.pkl"
        default_path = BASE_DIR / "storage" / "vector_db" / "index.pkl"
    return cache_path if cache_path.exists() else default_path


def index_exists(domain: Optional[str] = None) -> bool:
    return get_index_path(domain).exists()
