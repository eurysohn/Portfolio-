import pickle
from pathlib import Path
from typing import Dict, List

from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_PATH = BASE_DIR / "storage" / "vector_db" / "index.pkl"
SUPPLY_INDEX_PATH = BASE_DIR / "storage" / "vector_db_supply" / "index.pkl"
DEMAND_INDEX_PATH = BASE_DIR / "storage" / "vector_db_demand" / "index.pkl"


def _resolve_index_path(domain: str | None) -> Path:
    if domain == "supply":
        return SUPPLY_INDEX_PATH
    if domain == "demand":
        return DEMAND_INDEX_PATH
    return INDEX_PATH


def _load_index(domain: str | None = None) -> Dict:
    index_path = _resolve_index_path(domain)
    if not index_path.exists():
        if domain:
            raise FileNotFoundError(
                f"Vector index missing for {domain}. Run: python build_process_rag.py"
            )
        raise FileNotFoundError("Vector index missing. Run: python build_kb.py")
    with index_path.open("rb") as f:
        return pickle.load(f)


def search(query: str, top_k: int = 3, domain: str | None = None) -> List[Dict]:
    index = _load_index(domain)
    vectorizer = index["vectorizer"]
    matrix = index["matrix"]
    chunks = index["chunks"]

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, matrix).flatten()
    ranked = scores.argsort()[::-1][:top_k]
    results = []
    for idx in ranked:
        results.append(
            {
                "chunk_id": chunks[idx]["chunk_id"],
                "source": chunks[idx]["source"],
                "score": float(scores[idx]),
                "text": chunks[idx]["text"],
                "page_text": chunks[idx].get("page_text", ""),
            }
        )
    return results
