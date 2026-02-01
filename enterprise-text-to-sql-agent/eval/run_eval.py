import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from text2sql_agent.agent import AgentConfig, Text2SQLAgent


@dataclass
class EvalCase:
    case_id: str
    question: str
    expected_sql: Optional[str]
    expected_sql_patterns: List[str]
    expected_outcome_type: str
    expected_result_assertions: List[Dict[str, Any]]


def _load_cases(path: Path) -> List[EvalCase]:
    cases: List[EvalCase] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            cases.append(
                EvalCase(
                    case_id=payload["id"],
                    question=payload["question"],
                    expected_sql=payload.get("expected_sql"),
                    expected_sql_patterns=payload.get("expected_sql_patterns", []),
                    expected_outcome_type=payload["expected_outcome_type"],
                    expected_result_assertions=payload.get("expected_result_assertions", []),
                )
            )
    return cases


def _normalize_sql(sql: Optional[str]) -> str:
    if not sql:
        return ""
    return re.sub(r"\s+", " ", sql.strip().lower())


def _sql_matches(case: EvalCase, actual_sql: Optional[str]) -> bool:
    normalized_actual = _normalize_sql(actual_sql)
    if case.expected_sql:
        return _normalize_sql(case.expected_sql) == normalized_actual
    for pattern in case.expected_sql_patterns:
        if re.search(pattern, normalized_actual):
            return True
    return False


def _get_path(payload: Dict[str, Any], path: str) -> Any:
    value: Any = payload
    for part in path.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def _assert_results(payload: Dict[str, Any], assertions: List[Dict[str, Any]]) -> bool:
    for assertion in assertions:
        target = _get_path(payload, assertion["path"])
        op = assertion["op"]
        if op == "not_null" and target is None:
            return False
        if op == "equals" and target != assertion["value"]:
            return False
        if op == "gt" and not (target is not None and target > assertion["value"]):
            return False
    return True


def run_eval() -> Dict[str, Any]:
    agent = Text2SQLAgent(AgentConfig(db_url="sqlite:///data/app.db"))
    cases = _load_cases(Path("eval/golden_set.jsonl"))

    sql_matches = 0
    exec_matches = 0
    sql_cases = 0
    exec_cases = 0
    clarify_hits = 0
    clarify_pred = 0
    safe_error_hits = 0
    safe_error_pred = 0
    latencies: List[float] = []
    cache_hits = 0

    for case in cases:
        start = time.perf_counter()
        response = agent.ask(case.question)
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
        cache_hits += int(response.get("cache_hit") is True)

        if case.expected_sql or case.expected_sql_patterns:
            sql_cases += 1
            if _sql_matches(case, response.get("sql")):
                sql_matches += 1
        if case.expected_result_assertions:
            exec_cases += 1
            if _assert_results(response, case.expected_result_assertions):
                exec_matches += 1

        if response.get("outcome_type") == "CLARIFY":
            clarify_pred += 1
            if case.expected_outcome_type == "CLARIFY":
                clarify_hits += 1
        if response.get("outcome_type") == "SAFE_ERROR":
            safe_error_pred += 1
            if case.expected_outcome_type == "SAFE_ERROR":
                safe_error_hits += 1

    avg_latency = sum(latencies) / max(len(latencies), 1)
    metrics = {
        "total_cases": len(cases),
        "sql_match_rate": sql_matches / max(sql_cases, 1),
        "exec_match_rate": exec_matches / max(exec_cases, 1),
        "clarify_precision": clarify_hits / max(clarify_pred, 1),
        "safe_error_rate": safe_error_hits / max(safe_error_pred, 1),
        "avg_latency_ms": avg_latency,
        "cache_hit_rate": cache_hits / max(len(cases), 1),
    }
    return metrics


if __name__ == "__main__":
    print(json.dumps(run_eval(), indent=2))
