from typing import Dict, List, Tuple

# Mock dictionary for demo purposes
SCM_DICT = {
    "scm": {
        "term": "SCM",
        "definition": "Supply Chain Management",
        "business_meaning": "End-to-end planning, sourcing, production, logistics, and fulfillment.",
        "formula": "N/A"
    },
    "otif": {
        "term": "OTIF",
        "definition": "On-Time In-Full",
        "business_meaning": "A key performance indicator that measures whether the supply chain was able to deliver the expected product in the quantity ordered at the place and time agreed upon.",
        "formula": "OTIF = % On-Time * % In-Full"
    },
    "eoq": {
        "term": "EOQ",
        "definition": "Economic Order Quantity",
        "business_meaning": "The ideal order quantity a company should purchase to minimize inventory costs such as holding costs, shortage costs, and order costs.",
        "formula": "sqrt((2 * D * S) / H)"
    },
    "otd": {
        "term": "OTD",
        "definition": "On-Time Delivery",
        "business_meaning": "Measures the share of deliveries made on or before the promised date.",
        "formula": "OTD = on_time_deliveries / total_deliveries"
    },
    "tms": {
        "term": "TMS",
        "definition": "Transportation Management System",
        "business_meaning": "Software that plans, executes, and optimizes the movement of goods.",
        "formula": "N/A"
    }
}

def lookup(query: str) -> Tuple[List[Dict], List[str]]:
    query_lower = query.lower()
    results = []
    related = []

    for term, data in SCM_DICT.items():
        if term in query_lower:
            results.append(data)
            related.append(term)

    return results, related
