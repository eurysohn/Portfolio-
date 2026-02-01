"""In-memory session state store."""

from __future__ import annotations

import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from runtime.config import SESSION_MAX_ENTRIES


@dataclass
class SessionEntry:
    ticket: str
    route: str
    confidence: float
    tool_results: list[dict[str, Any]]
    escalated: bool
    timestamp: float


@dataclass
class SessionState:
    session_id: str
    history: list[SessionEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "history": [asdict(entry) for entry in self.history],
        }


class MemoryStore:
    def __init__(self, max_entries: int = SESSION_MAX_ENTRIES) -> None:
        self.max_entries = max_entries
        self._sessions: dict[str, SessionState] = {}
        self._lock = threading.Lock()

    def get_or_create(self, session_id: str) -> SessionState:
        with self._lock:
            return self._sessions.setdefault(session_id, SessionState(session_id=session_id))

    def append(self, session_id: str, entry: SessionEntry) -> SessionState:
        with self._lock:
            state = self._sessions.setdefault(session_id, SessionState(session_id=session_id))
            state.history.append(entry)
            if len(state.history) > self.max_entries:
                state.history = state.history[-self.max_entries :]
            return state

    def summary(self, session_id: str) -> dict[str, Any]:
        state = self.get_or_create(session_id)
        return {
            "session_id": session_id,
            "history_len": len(state.history),
            "last_route": state.history[-1].route if state.history else None,
            "last_escalated": state.history[-1].escalated if state.history else None,
            "last_updated_ts": state.history[-1].timestamp if state.history else None,
        }


memory_store = MemoryStore()


def now_ts() -> float:
    return time.time()
