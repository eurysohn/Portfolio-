from typing import Dict, List

INTENTS = ["PLANNING", "INVENTORY", "LOGISTICS", "DEFINITION", "CALCULATION", "GENERAL"]

KEYWORDS = {
    "PLANNING": [
        "forecast",
        "s&op",
        "sales and operations",
        "demand plan",
        "capacity",
        "수요예측",
        "수요 계획",
        "판매 운영",
        "s&op",
    ],
    "INVENTORY": [
        "inventory",
        "safety stock",
        "reorder",
        "cycle count",
        "abc",
        "재고",
        "안전재고",
        "재주문",
        "재주문점",
        "재고회전",
    ],
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
    "CALCULATION": [
        "calculate",
        "compute",
        "formula",
        "eoq",
        "reorder point",
        "fill rate",
        "계산",
        "산출",
        "공식",
    ],
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
