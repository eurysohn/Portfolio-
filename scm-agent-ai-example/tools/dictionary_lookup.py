import json
from difflib import get_close_matches
from pathlib import Path
from typing import Dict, List, Tuple


BASE_DIR = Path(__file__).resolve().parents[1]
DICT_PATH = BASE_DIR / "data" / "scm_dictionary.json"


def _load_dictionary() -> List[Dict]:
    raw = DICT_PATH.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        data = _parse_first_json_array(raw)
        return data if isinstance(data, list) else []


def _parse_first_json_array(text: str):
    start = text.find("[")
    if start == -1:
        return []
    depth = 0
    in_string = False
    escape = False
    for idx in range(start, len(text)):
        char = text[idx]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : idx + 1])
                except json.JSONDecodeError:
                    return []
    return []


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
