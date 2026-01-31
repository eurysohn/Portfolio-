from typing import Dict, List

INTENTS = ["PLANNING", "INVENTORY", "LOGISTICS", "DEFINITION", "CALCULATION", "GENERAL"]

KEYWORDS = {
    "PLANNING": ["forecast", "s&op", "sales and operations", "demand plan", "capacity"],
    "INVENTORY": ["inventory", "safety stock", "reorder", "cycle count", "abc"],
    "LOGISTICS": ["transport", "freight", "warehouse", "delivery", "carrier"],
    "DEFINITION": [
        "define",
        "what is",
        "meaning",
        "term",
        "glossary",
        "정의",
        "뜻",
        "의미",
        "뭐야",
        "무엇",
    ],
    "CALCULATION": ["calculate", "compute", "formula", "eoq", "reorder point", "fill rate"],
}


def route(query: str, related_terms: List[str]) -> Dict:
    text = query.lower()
    scores = {intent: 0.0 for intent in INTENTS}

    for intent, words in KEYWORDS.items():
        for word in words:
            if word in text:
                scores[intent] += 0.3

    if related_terms:
        scores["DEFINITION"] += 0.2

    if any(term.lower() in text for term in related_terms):
        scores["DEFINITION"] += 0.3

    if max(scores.values()) == 0:
        scores["GENERAL"] = 0.4

    intent = max(scores, key=scores.get)
    confidence = min(0.95, scores[intent] + 0.4)
    return {"intent": intent, "confidence": confidence}
