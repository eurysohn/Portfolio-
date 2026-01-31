import json
import pickle
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlparse

from sklearn.feature_extraction.text import TfidfVectorizer


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw_data"
PROCESS_DIR = DATA_DIR / "process_data"
SUPPLY_LIST_PATH = DATA_DIR / "url_list_supply.json"
DEMAND_LIST_PATH = DATA_DIR / "url_list_demand.json"
SEED_URLS_PATH = RAW_DIR / "seed_urls.json"
URL_LIST_PATH = DATA_DIR / "url_list.json"

SUPPLY_INDEX_DIR = BASE_DIR / "storage" / "vector_db_supply"
DEMAND_INDEX_DIR = BASE_DIR / "storage" / "vector_db_demand"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _chunk_text(text: str, min_words: int = 600, max_words: int = 900) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    step = max_words
    while start < len(words):
        end = min(start + step, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end
    return chunks


def _load_url_list(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    urls: List[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                url = item.strip()
            elif isinstance(item, dict):
                url = str(item.get("url", "")).strip()
            else:
                continue
            if url:
                urls.append(url)
    elif isinstance(data, dict):
        for item in data.get("seed_urls", []):
            if isinstance(item, str):
                url = item.strip()
            else:
                continue
            if url:
                urls.append(url)
    return urls


def _load_all_urls() -> List[str]:
    sources = [SUPPLY_LIST_PATH, DEMAND_LIST_PATH, SEED_URLS_PATH, URL_LIST_PATH]
    seen: set[str] = set()
    urls: List[str] = []
    for path in sources:
        for url in _load_url_list(path):
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def _safe_filename(url: str, index: int) -> str:
    path_name = Path(urlparse(url).path).name or "file"
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", path_name).strip("_")
    if not safe_name:
        safe_name = "file"
    return f"{index:03d}_{safe_name}"


def _url_index_map(urls: Iterable[str]) -> Dict[str, int]:
    return {url: idx for idx, url in enumerate(urls, start=1)}


def _match_raw_file(index: int) -> Optional[Path]:
    candidates = sorted(RAW_DIR.glob(f"{index:03d}_*"))
    return candidates[0] if candidates else None


def _collect_docs(urls: Iterable[str]) -> List[Dict[str, str]]:
    ordered_urls = _load_all_urls()
    index_map = _url_index_map(ordered_urls)
    docs: List[Dict[str, str]] = []
    for url in urls:
        idx = index_map.get(url)
        if not idx:
            continue
        raw_path = _match_raw_file(idx)
        if not raw_path:
            continue
        processed_path = PROCESS_DIR / f"{raw_path.stem}.txt"
        if not processed_path.exists():
            continue
        text = _normalize_text(processed_path.read_text(encoding="utf-8", errors="ignore"))
        if not text:
            continue
        docs.append(
            {
                "id": processed_path.stem,
                "source": str(raw_path),
                "text": text,
            }
        )
    return docs


def _build_vector_index(docs: List[Dict[str, str]], out_dir: Path) -> None:
    chunks = []
    for doc in docs:
        for idx, chunk in enumerate(_chunk_text(doc["text"])):
            chunks.append(
                {
                    "chunk_id": f"{doc['id']}_chunk_{idx}",
                    "source": doc["source"],
                    "text": chunk,
                }
            )
    texts = [c["text"] for c in chunks]
    if not texts:
        raise RuntimeError("No documents available to build the vector index.")
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)

    out_dir.mkdir(parents=True, exist_ok=True)
    index_path = out_dir / "index.pkl"
    with index_path.open("wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}, f)


def main() -> None:
    if not PROCESS_DIR.exists():
        raise RuntimeError("Missing process_data directory. Run: python process_data.py")

    supply_urls = _load_url_list(SUPPLY_LIST_PATH)
    demand_urls = _load_url_list(DEMAND_LIST_PATH)

    supply_docs = _collect_docs(supply_urls)
    demand_docs = _collect_docs(demand_urls)

    _build_vector_index(supply_docs, SUPPLY_INDEX_DIR)
    _build_vector_index(demand_docs, DEMAND_INDEX_DIR)

    print(
        f"Built supply index with {len(supply_docs)} docs and demand index with {len(demand_docs)} docs."
    )


if __name__ == "__main__":
    main()
