import pickle
from pathlib import Path
from typing import Dict, List

from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_PATH = BASE_DIR / "storage" / "vector_db" / "index.pkl"


def _load_index() -> Dict:
    if not INDEX_PATH.exists():
        raise FileNotFoundError("Vector index missing. Run: python build_kb.py")
    with INDEX_PATH.open("rb") as f:
        return pickle.load(f)


def search(query: str, top_k: int = 3) -> List[Dict]:
    index = _load_index()
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
