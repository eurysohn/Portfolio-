"""Optional LLM adapter interface (disabled by default)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str


class LLMAdapter:
    def generate(self, prompt: str) -> LLMResponse:
        raise NotImplementedError


class DisabledLLMAdapter(LLMAdapter):
    def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(text="LLM adapter disabled. Using rule-based runtime.")
