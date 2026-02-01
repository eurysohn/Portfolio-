"""Security utilities: PII redaction and prompt injection guardrails."""

from __future__ import annotations

import re
from dataclasses import dataclass


PII_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}

INJECTION_PATTERNS = [
    re.compile(r"ignore (all|previous) instructions", re.IGNORECASE),
    re.compile(r"system prompt", re.IGNORECASE),
    re.compile(r"developer message", re.IGNORECASE),
    re.compile(r"do anything now", re.IGNORECASE),
    re.compile(r"exfiltrate", re.IGNORECASE),
]


@dataclass
class GuardrailResult:
    sanitized_text: str
    blocked: bool
    reason: str | None


def redact_pii(text: str) -> str:
    redacted = text
    for label, pattern in PII_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{label.upper()}]", redacted)
    return redacted


def guardrails_check(text: str) -> GuardrailResult:
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return GuardrailResult(
                sanitized_text=text,
                blocked=True,
                reason="prompt_injection_detected",
            )
    return GuardrailResult(sanitized_text=text, blocked=False, reason=None)
