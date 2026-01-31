import argparse
import json
from pathlib import Path

from agent import run_agent
from build_kb import main as build_kb


def _ensure_index():
    index_path = Path(__file__).resolve().parent / "storage" / "vector_db" / "index.pkl"
    if not index_path.exists():
        build_kb()


def _format_response(result):
    return json.dumps(
        {
            "Answer": result["Answer"],
            "Sources": result["Sources"],
            "Confidence": result["Confidence"],
            "Domain": result["Domain"],
        },
        indent=2,
    )


def main():
    parser = argparse.ArgumentParser(description="Run the SCM enterprise agent.")
    parser.add_argument("--query", type=str, help="Question to ask the agent.")
    args = parser.parse_args()

    _ensure_index()

    if args.query:
        result = run_agent(args.query)
        print(_format_response(result))
        return

    print("SCM Agent (type 'exit' to quit)")
    while True:
        query = input(">> ").strip()
        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue
        result = run_agent(query)
        print(_format_response(result))


if __name__ == "__main__":
    main()
