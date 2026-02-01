"""CLI for the agent runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from observability.tracing import trace_store
from runtime.engine import AgentRuntime


def _serialize_result(result: Any) -> dict[str, Any]:
    payload = result.__dict__
    payload["tool_results"] = [tool.__dict__ for tool in result.tool_results]
    payload["tool_calls"] = [call.__dict__ for call in result.tool_calls]
    return payload


def _print_result(result: Any) -> None:
    print(json.dumps(_serialize_result(result), indent=2))


def run_interactive(correlation_id: str | None = None, idempotency_key: str | None = None) -> None:
    runtime = AgentRuntime()
    ticket = input("Enter ticket: ").strip()
    result = runtime.run(ticket, correlation_id=correlation_id, idempotency_key=idempotency_key)
    _print_result(result)


def run_demo() -> None:
    runtime = AgentRuntime()
    sample_path = Path("examples/sample_tickets.jsonl")
    for line in sample_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        result = runtime.run(
            payload["ticket"],
            correlation_id=payload.get("id"),
            idempotency_key=payload.get("idempotency_key"),
        )
        _print_result(result)


def show_trace(run_id: str) -> None:
    events = trace_store.get_run(run_id)
    if not events:
        events = trace_store.load_from_jsonl(run_id)
    print(json.dumps([event.__dict__ for event in events], indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini agent runtime CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--correlation-id")
    run_parser.add_argument("--idempotency-key")
    subparsers.add_parser("demo")

    show_parser = subparsers.add_parser("show-trace")
    show_parser.add_argument("run_id")

    args = parser.parse_args()

    if args.command == "run":
        run_interactive(correlation_id=args.correlation_id, idempotency_key=args.idempotency_key)
    elif args.command == "demo":
        run_demo()
    elif args.command == "show-trace":
        show_trace(args.run_id)


if __name__ == "__main__":
    main()
