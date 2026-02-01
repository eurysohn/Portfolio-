"""Mock on-call notification tool."""

from __future__ import annotations

from typing import Any


def notify_oncall(args: dict[str, Any]) -> dict[str, Any]:
    ticket = str(args.get("ticket", ""))
    return {"notified": True, "summary": ticket[:120]}
