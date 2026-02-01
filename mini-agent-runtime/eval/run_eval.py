"""Run golden set evaluation."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from eval.judge import judge_case
from runtime.engine import AgentRuntime


def _serialize_result(result: Any) -> dict[str, Any]:
    payload = result.__dict__
    payload["tool_results"] = [tool.__dict__ for tool in result.tool_results]
    payload["tool_calls"] = [call.__dict__ for call in result.tool_calls]
    return payload


def run_eval() -> None:
    runtime = AgentRuntime()
    cases = []
    for line in Path("eval/golden_set.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))

    total = len(cases)
    passed = 0
    tool_successes = 0
    fallback = 0
    latencies = []

    for case in cases:
        start = time.time()
        result = runtime.run(case["ticket"], correlation_id=case["id"])
        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)
        serialized = _serialize_result(result)
        verdict = judge_case(case, serialized)
        if verdict["passed"]:
            passed += 1
        if verdict["tool_success"]:
            tool_successes += 1
        if serialized["escalate"] and not case["expected_escalate"]:
            fallback += 1

    metrics = {
        "pass_rate": passed / total if total else 0.0,
        "tool_success_rate": tool_successes / total if total else 0.0,
        "fallback_rate": fallback / total if total else 0.0,
        "avg_latency_ms": sum(latencies) / total if total else 0.0,
    }
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    run_eval()
