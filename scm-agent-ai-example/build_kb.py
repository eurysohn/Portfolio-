import hashlib
import json
from pathlib import Path

import joblib
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer

from data.build_synthetic_docs import generate_docs


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "enterprise_knowledge"
VECTOR_DIR = BASE_DIR / "storage" / "vector_db"


def _ensure_dictionary():
    dict_path = DATA_DIR / "scm_dictionary.json"
    if dict_path.exists():
        return
    fallback = [
        {
            "term": "OTIF",
            "definition": "On Time In Full: orders delivered on time and complete.",
            "business_meaning": "Core customer service metric.",
            "formula": "OTIF = on-time and in-full orders / total orders * 100",
            "synonyms": ["on-time in-full"],
            "example_queries": ["What is OTIF?"],
        }
    ]
    dict_path.write_text(json.dumps(fallback, indent=2), encoding="utf-8")


def _load_seed_urls():
    seed_path = DATA_DIR / "seed_urls.json"
    if not seed_path.exists():
        return []
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    return data.get("seed_urls", [])


def _crawl_seed_urls():
    seed_urls = _load_seed_urls()
    if not seed_urls:
        return []
    KB_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for url in seed_urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join(soup.get_text(separator=" ").split())
            url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]
            filename = f"seed_{url_hash}.txt"
            (KB_DIR / filename).write_text(text, encoding="utf-8")
            saved.append(filename)
        except Exception:
            continue
    return saved


def _chunk_text(text, min_tokens=600, max_tokens=900):
    tokens = text.split()
    if not tokens:
        return []
    chunks = []
    start = 0
    target = (min_tokens + max_tokens) // 2
    while start < len(tokens):
        end = min(start + target, len(tokens))
        if end - start < min_tokens and end < len(tokens):
            end = min(start + max_tokens, len(tokens))
        chunk = " ".join(tokens[start:end])
        chunks.append(chunk)
        start = end
    return chunks


def _build_index():
    KB_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    docs = []
    for path in sorted(KB_DIR.glob("*.txt")):
        docs.append((path.name, path.read_text(encoding="utf-8")))

    chunks = []
    for source, text in docs:
        for i, chunk in enumerate(_chunk_text(text)):
            chunks.append(
                {"text": chunk, "metadata": {"source": source, "chunk_id": i}}
            )

    if not chunks:
        raise RuntimeError("No documents found to index.")

    vectorizer = TfidfVectorizer(stop_words="english", max_features=40000)
    matrix = vectorizer.fit_transform([c["text"] for c in chunks])

    index = {"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}
    joblib.dump(index, VECTOR_DIR / "index.pkl")

    _build_sentence_transformer_embeddings(chunks)


def _build_sentence_transformer_embeddings(chunks):
    try:
        from sentence_transformers import SentenceTransformer
    except Exception:
        return
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    embeddings = model.encode([c["text"] for c in chunks])
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    (VECTOR_DIR / "st_model_name.txt").write_text(model_name, encoding="utf-8")
    import numpy as np

    np.save(VECTOR_DIR / "st_embeddings.npy", embeddings)


def main():
    _ensure_dictionary()
    generate_docs(KB_DIR)
    _crawl_seed_urls()
    _build_index()
    print("Knowledge base built successfully.")


if __name__ == "__main__":
    main()
