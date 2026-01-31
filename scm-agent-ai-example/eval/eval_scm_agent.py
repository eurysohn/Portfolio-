import json
from pathlib import Path
from typing import Dict, List

from agent.engine import run_agent


BASE_DIR = Path(__file__).resolve().parents[1]
GOLDEN_PATH = BASE_DIR / "data" / "scm_golden_set.json"


def _load_golden() -> List[Dict]:
    data = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _keyword_match(answer: str, keywords: List[str]) -> bool:
    answer_lower = answer.lower()
    return all(k.lower() in answer_lower for k in keywords)


def evaluate() -> None:
    golden = _load_golden()
    total = len(golden)
    if total == 0:
        print("Golden set is empty.")
        return

    correct = 0
    grounded = 0
    routing_correct = 0

    for row in golden:
        result = run_agent(row["query"])
        if _keyword_match(result["answer"], row["expected_keywords"]):
            correct += 1
        if result["sources"]:
            grounded += 1
        if result["domain"] == row["expected_intent"]:
            routing_correct += 1

    print(f"Overall accuracy: {correct / total:.2%}")
    print(f"Grounding rate: {grounded / total:.2%}")
    print(f"Routing accuracy: {routing_correct / total:.2%}")


if __name__ == "__main__":
    evaluate()
