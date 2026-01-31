import json
import re
import uuid
from pathlib import Path
from typing import Dict, List

from agent.prompts import ANSWER_TEMPLATE, SYSTEM_PROMPT
from agent.router import route
from tools.calculators import economic_order_quantity, fill_rate, otif, reorder_point, safety_stock
from tools.dictionary_lookup import lookup
from tools.rag_search import search


BASE_DIR = Path(__file__).resolve().parents[1]
LOG_PATH = BASE_DIR / "logs" / "scm_runs.jsonl"


def _format_sources(sources: List[Dict]) -> str:
    if not sources:
        return "None"
    return "\n".join(f"- {s['source']} (score={s['score']:.3f})" for s in sources)


def _log_run(payload: Dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")


def _run_calculator(query: str) -> Dict:
    text = query.lower()
    if "eoq" in text:
        return economic_order_quantity(annual_demand=12000, order_cost=50, holding_cost=5)
    if "reorder point" in text:
        return reorder_point(daily_demand=120, lead_time_days=10, safety_stock=300)
    if "safety stock" in text:
        return safety_stock(z_score=1.65, demand_std=40, lead_time_days=10)
    if "fill rate" in text:
        return fill_rate(filled_units=950, total_demand_units=1000)
    if "otif" in text:
        return otif(on_time=0.92, in_full=0.95)
    return {"metric": "Calculation", "value": "Provide parameters for calculation."}


def _detect_rag_domain(query: str) -> str | None:
    text = query.lower()
    demand_keywords = [
        "demand",
        "forecast",
        "s&op",
        "sales and operations",
        "sales & operations",
        "demand planning",
    ]
    supply_keywords = [
        "supply",
        "supplier",
        "procurement",
        "logistics",
        "transport",
        "warehouse",
    ]
    if any(word in text for word in demand_keywords):
        return "demand"
    if any(word in text for word in supply_keywords):
        return "supply"
    return None


def _summarize_context(text: str, max_sentences: int = 3) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    summary = " ".join(sentences[:max_sentences]).strip()
    return summary


def run_agent(query: str, confidence_threshold: float = 0.55, top_k: int = 3) -> Dict:
    dict_results, related_terms = lookup(query)
    routing = route(query, related_terms)
    intent = routing["intent"]
    confidence = routing["confidence"]
    sources = []
    answer = ""
    tool_calls = []
    handled = False

    if intent == "DEFINITION":
        if dict_results:
            entry = dict_results[0]
            answer = (
                f"{entry['term']}: {entry['definition']}\n"
                f"Business meaning: {entry['business_meaning']}\n"
                f"Formula: {entry.get('formula', 'N/A')}"
            )
            sources = [
                {
                    "chunk_id": f"dict:{entry['term']}",
                    "source": "data/scm_dictionary.json",
                    "score": 1.0,
                    "text": entry["term"],
                    "page_text": "",
                }
            ]
            tool_calls.append("dictionary_lookup")
            handled = True
        else:
            text = query.lower()
            if "scm" in text or "supply chain" in text:
                answer = (
                    "SCM (Supply Chain Management) is the end-to-end management of "
                    "planning, sourcing, production, logistics, and fulfillment to "
                    "deliver products efficiently and reliably."
                )
                tool_calls.append("definition_fallback")
                sources = [
                    {
                        "chunk_id": "built_in_definition",
                        "source": "built_in_definition",
                        "score": 1.0,
                        "text": "SCM",
                        "page_text": "",
                    }
                ]
                handled = True
            else:
                intent = "GENERAL"

    if intent == "CALCULATION":
        calc = _run_calculator(query)
        answer = f"{calc['metric']} = {calc['value']}"
        tool_calls.append("calculator")
        handled = True

    if not handled:
        domain = _detect_rag_domain(query)
        sources = search(query, top_k=top_k, domain=domain)
        context_blocks = []
        for s in sources:
            if s.get("page_text"):
                context_blocks.append(s["page_text"])
            else:
                context_blocks.append(s["text"])
        context = " ".join(context_blocks)[:2000]
        summary = _summarize_context(context, max_sentences=3)
        answer = summary if summary else "No relevant information found in sources."
        tool_calls.append("rag_search")

    if confidence < confidence_threshold:
        related = ", ".join(related_terms[:5]) if related_terms else "No related terms found"
        answer = (
            "I want to be precise. Can you clarify your request? "
            f"Related terms: {related}"
        )
        sources = []

    formatted = ANSWER_TEMPLATE.format(
        answer=answer,
        sources=_format_sources(sources),
        confidence=confidence,
        domain=intent,
    )

    payload = {
        "run_id": str(uuid.uuid4()),
        "query": query,
        "intent": intent,
        "tool_calls": tool_calls,
        "sources": [s["source"] for s in sources],
        "confidence": confidence,
        "answer": answer,
    }
    _log_run(payload)

    return {"answer": answer, "sources": sources, "confidence": confidence, "domain": intent, "formatted": formatted}
