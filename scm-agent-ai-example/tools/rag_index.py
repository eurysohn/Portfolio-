import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parents[1]
KB_DIR = BASE_DIR / "data" / "knowledge_base"
INDEX_DIR = BASE_DIR / "data" / "index"
VECTORIZER_PATH = INDEX_DIR / "vectorizer.joblib"
MATRIX_PATH = INDEX_DIR / "tfidf.joblib"
METADATA_PATH = INDEX_DIR / "metadata.jsonl"


@dataclass
class RagIndex:
    vectorizer: TfidfVectorizer
    matrix: object
    metadata: List[Dict]


def _iter_docs() -> Iterable[Tuple[str, str]]:
    for path in sorted(KB_DIR.glob("**/*")):
        if path.is_dir():
            continue
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        yield path.stem, content


def _chunk_text(text: str, max_chars: int = 800) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    idx = 0
    while idx < len(paragraphs):
        para = paragraphs[idx]
        if para.startswith("#") and len(para) < 60 and idx + 1 < len(paragraphs):
            para = f"{para}\n{paragraphs[idx + 1]}"
            idx += 2
        else:
            idx += 1
        if len(para) <= max_chars:
            chunks.append(para)
            continue
        start = 0
        while start < len(para):
            end = min(start + max_chars, len(para))
            chunks.append(para[start:end])
            start = end
    return chunks


def build_index() -> RagIndex:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    docs: List[str] = []
    metadata: List[Dict] = []
    for doc_id, content in _iter_docs():
        for idx, chunk in enumerate(_chunk_text(content)):
            docs.append(chunk)
            metadata.append(
                {
                    "source_id": doc_id,
                    "chunk_id": f"{doc_id}::chunk_{idx}",
                    "text": chunk,
                }
            )
    if not docs:
        raise RuntimeError("No knowledge base documents found to index.")

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(docs)

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(matrix, MATRIX_PATH)
    with METADATA_PATH.open("w", encoding="utf-8") as f:
        for row in metadata:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")

    return RagIndex(vectorizer=vectorizer, matrix=matrix, metadata=metadata)


def load_index() -> RagIndex:
    if not VECTORIZER_PATH.exists() or not MATRIX_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError("RAG index missing. Run scripts/build_rag_index.py first.")
    vectorizer = joblib.load(VECTORIZER_PATH)
    matrix = joblib.load(MATRIX_PATH)
    metadata: List[Dict] = []
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                metadata.append(json.loads(line))
    return RagIndex(vectorizer=vectorizer, matrix=matrix, metadata=metadata)


def search_index(query: str, top_k: int = 3) -> List[Dict]:
    index = load_index()
    query_vec = index.vectorizer.transform([query])
    scores = cosine_similarity(query_vec, index.matrix).flatten()
    query_tokens = {
        token
        for token in re.split(r"[^a-zA-Z0-9가-힣]+", query.lower())
        if token
    }
    top_indices = scores.argsort()[::-1][:top_k]
    results: List[Dict] = []
    for idx in top_indices:
        meta = index.metadata[idx]
        text_tokens = {
            token
            for token in re.split(r"[^a-zA-Z0-9가-힣]+", meta["text"].lower())
            if token
        }
        overlap = len(query_tokens & text_tokens)
        score = float(scores[idx]) + (0.15 * overlap)
        results.append(
            {
                "source_id": meta["source_id"],
                "chunk_id": meta["chunk_id"],
                "score": score,
                "text": meta["text"],
                "page_text": meta["text"],
            }
        )
    return results
