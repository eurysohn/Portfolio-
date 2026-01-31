import pickle
from typing import Dict, List, Optional

from sklearn.metrics.pairwise import cosine_similarity

from config import get_index_path


def _load_index(domain: Optional[str] = None) -> Dict:
    index_path = get_index_path(domain)
    if not index_path.exists():
        if domain:
            raise FileNotFoundError(
                f"Vector index missing for {domain}. Run: python build_process_rag.py"
            )
        supply_path = get_index_path("supply")
        demand_path = get_index_path("demand")
        if supply_path.exists():
            index_path = supply_path
        elif demand_path.exists():
            index_path = demand_path
        else:
            raise FileNotFoundError("Vector index missing. Run: python build_process_rag.py")
    with index_path.open("rb") as f:
        return pickle.load(f)


def search(query: str, top_k: int = 3, domain: Optional[str] = None) -> List[Dict]:
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
