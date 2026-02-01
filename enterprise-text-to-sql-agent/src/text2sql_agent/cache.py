import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


def normalize_question(question: str) -> str:
    return " ".join(question.lower().strip().split())


def cache_key(question: str, schema_hash: str, scope: str) -> str:
    normalized = normalize_question(question)
    raw = f"{normalized}|{schema_hash}|{scope}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class CacheEntry:
    response: Dict[str, Any]


class FileCache:
    def __init__(self, path: str = ".cache/agent_cache.json") -> None:
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self, payload: Dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)

    def get(self, key: str) -> Optional[CacheEntry]:
        payload = self._load()
        if key not in payload:
            return None
        return CacheEntry(response=payload[key])

    def set(self, key: str, entry: CacheEntry | Dict[str, Any]) -> None:
        payload = self._load()
        if isinstance(entry, CacheEntry):
            payload[key] = entry.response
        else:
            payload[key] = entry
        self._save(payload)
