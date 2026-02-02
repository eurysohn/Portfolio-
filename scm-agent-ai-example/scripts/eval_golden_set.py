import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from agent.engine import run_agent  # noqa: E402
from tools.rag_index import build_index, load_index  # noqa: E402

GOLDEN_PATH = BASE_DIR / "data" / "golden_set_synth.jsonl"


def _ensure_index() -> None:
    try:
        load_index()
    except FileNotFoundError:
        build_index()


def _route_match(expected: List[str], actual: List[str]) -> bool:
    return all(route in actual for route in expected)


def _retrieval_hit(expected_sources: List[str], trace: Dict) -> bool:
    if not expected_sources:
        return True
    if "structured_kpis" in expected_sources:
        return "data_query" in trace.get("tools_used", [])
    hits = trace.get("retrieval_hits", [])
    sources = {hit.get("source_id", "") for hit in hits}
    return any(expected in source for expected in expected_sources for source in sources)


def _keypoint_match(expected_keypoints: List[str], answer: str, min_hits: int = 2) -> bool:
    if not expected_keypoints:
        return True
    lowered = answer.lower()
    hits = [kp for kp in expected_keypoints if kp.lower() in lowered]
    return len(hits) >= min(min_hits, len(expected_keypoints))


def evaluate() -> Tuple[int, int, List[Dict]]:
    _ensure_index()
    total = 0
    passed = 0
    failures: List[Dict] = []

    with GOLDEN_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            sample = json.loads(line)
            total += 1

            result = run_agent(sample["question"], top_k=3)
            trace = result.get("trace", {})
            actual_route = trace.get("route_taken", [])

            route_ok = _route_match(sample["expected_route"], actual_route)
            retrieval_ok = _retrieval_hit(sample.get("expected_sources_hint", []), trace)
            keypoints_ok = _keypoint_match(sample.get("expected_answer_keypoints", []), result["answer"])

            if route_ok and retrieval_ok and keypoints_ok:
                passed += 1
                continue

            failures.append(
                {
                    "id": sample["id"],
                    "route_ok": route_ok,
                    "retrieval_ok": retrieval_ok,
                    "keypoints_ok": keypoints_ok,
                    "expected_route": sample["expected_route"],
                    "actual_route": actual_route,
                    "expected_sources_hint": sample.get("expected_sources_hint", []),
                    "answer_snippet": result["answer"][:160],
                }
            )

    return passed, total, failures


def main() -> None:
    passed, total, failures = evaluate()
    print(f"Golden set: {passed}/{total} passed")
    if failures:
        print("\nFailures:")
        for failure in failures[:20]:
            print(json.dumps(failure, ensure_ascii=True))


if __name__ == "__main__":
    main()
