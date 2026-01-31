import json
import re
from difflib import SequenceMatcher
from pathlib import Path


_DICT_CACHE = None


def _normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _load_dictionary():
    global _DICT_CACHE
    if _DICT_CACHE is not None:
        return _DICT_CACHE

    dict_path = Path(__file__).resolve().parents[1] / "data" / "scm_dictionary.json"
    entries = json.loads(dict_path.read_text(encoding="utf-8"))

    expanded = []
    for entry in entries:
        term = entry["term"]
        expanded.append((_normalize(term), entry))
        for syn in entry.get("synonyms", []):
            expanded.append((_normalize(syn), entry))

    _DICT_CACHE = (entries, expanded)
    return _DICT_CACHE


def lookup_terms(query, top_n=5):
    _, expanded = _load_dictionary()
    qn = _normalize(query)

    scored = []
    for token, entry in expanded:
        if not token:
            continue
        ratio = SequenceMatcher(None, qn, token).ratio()
        if token in qn or qn in token:
            ratio = max(ratio, 0.75)
        scored.append((ratio, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    seen = set()
    results = []
    for score, entry in scored:
        if entry["term"] in seen:
            continue
        seen.add(entry["term"])
        results.append({"score": round(score, 3), **entry})
        if len(results) >= top_n:
            break

    return results


def related_terms(query, top_n=5):
    results = lookup_terms(query, top_n=top_n)
    return [r["term"] for r in results]
