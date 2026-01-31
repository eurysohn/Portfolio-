import json
from difflib import get_close_matches
from pathlib import Path
from typing import Dict, List, Tuple


BASE_DIR = Path(__file__).resolve().parents[1]
DICT_PATH = BASE_DIR / "data" / "scm_dictionary.json"


def _load_dictionary() -> List[Dict]:
    data = json.loads(DICT_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _build_index(entries: List[Dict]) -> Dict[str, str]:
    index = {}
    for entry in entries:
        term = entry.get("term", "").strip().lower()
        if term:
            index[term] = entry["term"]
        for syn in entry.get("synonyms", []):
            syn_key = str(syn).strip().lower()
            if syn_key:
                index[syn_key] = entry["term"]
    return index


def lookup(query: str, top_k: int = 5) -> Tuple[List[Dict], List[str]]:
    entries = _load_dictionary()
    index = _build_index(entries)
    query_norm = query.strip().lower()

    related_terms = []
    if query_norm in index:
        related_terms.append(index[query_norm])

    term_keys = list(index.keys())
    fuzzy = get_close_matches(query_norm, term_keys, n=top_k, cutoff=0.6)
    for match in fuzzy:
        related_terms.append(index[match])

    related_terms = list(dict.fromkeys(related_terms))
    results = [e for e in entries if e.get("term") in related_terms]
    return results, related_terms
