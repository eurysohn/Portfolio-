import json
import re
import urllib.request
from pathlib import Path
from typing import List
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw_data"
SEED_URLS_PATH = DATA_DIR / "seed_urls.json"
URL_LIST_PATH = DATA_DIR / "url_list.json"
URL_LIST_SUPPLY_PATH = DATA_DIR / "url_list_supply.json"
URL_LIST_DEMAND_PATH = DATA_DIR / "url_list_demand.json"


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
    sources = [
        URL_LIST_SUPPLY_PATH,
        URL_LIST_DEMAND_PATH,
        SEED_URLS_PATH,
        URL_LIST_PATH,
    ]
    seen: set[str] = set()
    urls: List[str] = []
    for path in sources:
        for url in _load_url_list(path):
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def _fetch_url_bytes(url: str) -> tuple[bytes, str]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "scm-agent-ai-example/1.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "")
            raw = response.read()
    except Exception:
        return b"", ""
    return raw, content_type


def _guess_extension(url: str, content_type: str) -> str:
    url_lower = url.lower()
    if "pdf" in content_type or url_lower.endswith(".pdf"):
        return ".pdf"
    if "presentation" in content_type or url_lower.endswith(".pptx"):
        return ".pptx"
    if "word" in content_type or url_lower.endswith(".docx"):
        return ".docx"
    return ".html"


def _safe_filename(url: str, ext: str, index: int) -> str:
    path_name = Path(urlparse(url).path).name or "file"
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", path_name).strip("_")
    if not safe_name:
        safe_name = "file"
    if not safe_name.lower().endswith(ext):
        safe_name = f"{safe_name}{ext}"
    return f"{index:03d}_{safe_name}"


def main() -> None:
    urls = _load_all_urls()
    if not urls:
        print("No URLs found to download.")
        return

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for i, url in enumerate(urls, start=1):
        data, content_type = _fetch_url_bytes(url)
        if not data:
            continue
        ext = _guess_extension(url, content_type)
        filename = _safe_filename(url, ext, i)
        path = RAW_DIR / filename
        if path.exists():
            continue
        path.write_bytes(data)

    print(f"Downloaded {len(list(RAW_DIR.iterdir()))} files into {RAW_DIR}")


if __name__ == "__main__":
    main()
