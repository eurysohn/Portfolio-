import os
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def _load_index():
    index_path = Path(__file__).resolve().parents[1] / "storage" / "vector_db" / "index.pkl"
    if not index_path.exists():
        raise FileNotFoundError("Vector index not found. Run python build_kb.py first.")
    return joblib.load(index_path)


def _try_sentence_transformers(query, index_dir):
    if os.getenv("SCM_EMBEDDING", "").lower() != "sentence_transformers":
        return None
    try:
        from sentence_transformers import SentenceTransformer
    except Exception:
        return None

    emb_path = Path(index_dir) / "st_embeddings.npy"
    model_path = Path(index_dir) / "st_model_name.txt"
    if not emb_path.exists() or not model_path.exists():
        return None

    model_name = model_path.read_text(encoding="utf-8").strip()
    model = SentenceTransformer(model_name)
    doc_embeddings = np.load(emb_path)
    query_vec = model.encode([query])
    scores = cosine_similarity(query_vec, doc_embeddings)[0]
    return scores


def rag_search(query, top_k=4):
    index = _load_index()
    vectorizer = index["vectorizer"]
    matrix = index["matrix"]
    chunks = index["chunks"]
    index_dir = Path(__file__).resolve().parents[1] / "storage" / "vector_db"

    scores = _try_sentence_transformers(query, index_dir)
    if scores is None:
        q_vec = vectorizer.transform([query])
        scores = cosine_similarity(q_vec, matrix)[0]

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    results = []
    for idx, score in ranked:
        meta = chunks[idx]["metadata"]
        results.append(
            {
                "score": round(float(score), 4),
                "text": chunks[idx]["text"],
                "source": meta["source"],
                "chunk_id": meta["chunk_id"],
            }
        )
    return results
