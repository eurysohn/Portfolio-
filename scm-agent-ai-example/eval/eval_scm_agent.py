import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent import run_agent
from build_kb import main as build_kb


def _ensure_index():
    index_path = Path(__file__).resolve().parents[1] / "storage" / "vector_db" / "index.pkl"
    if not index_path.exists():
        build_kb()


def _keyword_match(answer, keywords):
    text = answer.lower()
    return all(k.lower() in text for k in keywords)


def main():
    _ensure_index()
    data_path = Path(__file__).resolve().parents[1] / "data" / "scm_golden_set.json"
    golden = json.loads(data_path.read_text(encoding="utf-8"))

    total = len(golden)
    correct = 0
    grounded = 0
    routed = 0

    for item in golden:
        result = run_agent(item["query"])
        if _keyword_match(result["Answer"], item["expected_keywords"]):
            correct += 1
        if result["Sources"]:
            grounded += 1
        if result["Domain"] == item["expected_intent"]:
            routed += 1

    accuracy = correct / total if total else 0
    grounding_rate = grounded / total if total else 0
    routing_accuracy = routed / total if total else 0

    print("SCM Agent Evaluation")
    print(f"Total queries: {total}")
    print(f"Keyword accuracy: {accuracy:.2f}")
    print(f"Grounding rate: {grounding_rate:.2f}")
    print(f"Routing accuracy: {routing_accuracy:.2f}")


if __name__ == "__main__":
    main()
