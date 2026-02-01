"""Tool registry creation."""

from __future__ import annotations

from runtime.models import Tool
from runtime.tooling import ToolRegistry
from tools.data_query import data_query
from tools.db_query import db_query
from tools.http_tool import http_request
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
            name="http_request",
            input_schema={
                "type": "object",
                "properties": {"method": {"type": "string"}, "path": {"type": "string"}},
            },
            invoke=http_request,
            description="Mock HTTP tool for checking service endpoints.",
        )
    )
    registry.register(
        Tool(
            name="db_query",
            input_schema={
                "type": "object",
                "properties": {"table": {"type": "string"}, "filters": {"type": "object"}},
            },
            invoke=db_query,
            description="Mock DB query tool for incident/ticket tables.",
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
