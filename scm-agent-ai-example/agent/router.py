from typing import Dict, List, Optional


def route(query: str, related_terms: Optional[List[str]] = None) -> Dict:
    query_lower = query.lower()

    if any(k in query_lower for k in ["latest month", "last month", "latest week", "last week", "kpi"]):
        return {"intent": "DATA_QUERY", "confidence": 0.8}

    # Simple keyword-based routing for now
    if any(k in query_lower for k in ["how to calculate", "formula", "calculator", "eoq", "otif", "reorder point"]):
        return {"intent": "CALCULATION", "confidence": 0.9}

    if any(k in query_lower for k in ["what is", "define", "definition", "meaning", "dictionary"]):
        return {"intent": "DEFINITION", "confidence": 0.9}

    if any(k in query_lower for k in ["forecast", "planning", "inventory", "supply", "demand"]):
        return {"intent": "PLANNING", "confidence": 0.8}

    return {"intent": "GENERAL", "confidence": 0.7}
