import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from tools.rag_index import build_index  # noqa: E402


def main() -> None:
    index = build_index()
    print(f"Indexed {len(index.metadata)} chunks.")


if __name__ == "__main__":
    main()
