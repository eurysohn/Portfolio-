import argparse
import sys
from pathlib import Path

from agent.engine import run_agent


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SCM agent locally.")
    parser.add_argument("query", nargs="*", help="Query to the SCM agent.")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    index_path = base_dir / "storage" / "vector_db" / "index.pkl"
    if not index_path.exists():
        print("Knowledge base not found. Run: python build_kb.py")
        return 1

    if args.query:
        query = " ".join(args.query).strip()
        result = run_agent(query)
        print(result["formatted"])
        return 0

    print("Enter queries (Ctrl+C to exit):")
    try:
        while True:
            query = input("> ").strip()
            if not query:
                continue
            result = run_agent(query)
            print(result["formatted"])
    except KeyboardInterrupt:
        print("\nExiting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
