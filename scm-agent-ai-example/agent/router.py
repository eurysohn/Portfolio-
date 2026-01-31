import re

INTENTS = [
    "PLANNING",
    "INVENTORY",
    "LOGISTICS",
    "DEFINITION",
    "CALCULATION",
    "GENERAL",
]

KEYWORDS = {
    "PLANNING": [
        "forecast",
        "demand planning",
        "s&op",
        "sop",
        "mps",
        "mrp",
        "capacity",
        "planning",
        "net requirements",
        "gross requirements",
        "allocation",
    ],
    "INVENTORY": [
        "inventory",
        "safety stock",
        "reorder",
        "rop",
        "fill rate",
        "cycle count",
        "stockout",
        "backorder",
        "turnover",
        "min-max",
    ],
    "LOGISTICS": [
        "logistics",
        "transport",
        "tms",
        "wms",
        "cross dock",
        "last mile",
        "freight",
        "carrier",
        "cold chain",
        "incoterms",
        "customs",
    ],
    "DEFINITION": [
        "what is",
        "define",
        "meaning",
        "explain",
        "definition",
    ],
    "CALCULATION": [
        "calculate",
        "compute",
        "formula",
        "how do i calculate",
        "equation",
        "solve",
    ],
}


def _normalize(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def route_intent(query):
    text = _normalize(query)
    scores = {intent: 0 for intent in INTENTS}

    for intent, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[intent] += 1

    if scores["CALCULATION"] > 0:
        scores["CALCULATION"] += 1
    if scores["DEFINITION"] > 0 and any(w in text for w in ["define", "what is", "meaning"]):
        scores["DEFINITION"] += 1

    best_intent = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = scores[best_intent] / total if total > 0 else 0.25

    if total == 0:
        best_intent = "GENERAL"
        confidence = 0.3

    return best_intent, round(confidence, 3)
