"""Tool registry creation."""

from __future__ import annotations

from runtime.models import Tool
from runtime.tooling import ToolRegistry
from tools.data_query import data_query
from tools.notify_oncall import notify_oncall
from tools.runbook_lookup import runbook_lookup


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="runbook_lookup",
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            invoke=runbook_lookup,
            description="Search runbooks for remediation steps.",
        )
    )
    registry.register(
        Tool(
            name="data_query",
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
            invoke=data_query,
            description="Query operational metrics.",
        )
    )
    registry.register(
        Tool(
            name="notify_oncall",
            input_schema={"type": "object", "properties": {"ticket": {"type": "string"}}},
            invoke=notify_oncall,
            description="Notify on-call engineer.",
        )
    )
    return registry
