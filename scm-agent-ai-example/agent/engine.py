import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agent.prompts import CLARIFICATION_PROMPT
from agent.router import route_intent
from tools.calculators import run_calculation
from tools.dictionary_lookup import lookup_terms, related_terms
from tools.rag_search import rag_search


CONFIDENCE_THRESHOLD = 0.45


def _first_sentences(text, max_sentences=2):
    parts = text.replace("\n", " ").split(". ")
    snippet = ". ".join(parts[:max_sentences]).strip()
    if not snippet.endswith("."):
        snippet += "."
    return snippet


def _log_run(payload):
    log_dir = Path(__file__).resolve().parents[1] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "scm_runs.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def run_agent(query):
    intent, intent_conf = route_intent(query)
    tool_calls = []
    sources = []
    answer = ""
    confidence = intent_conf

    if intent == "DEFINITION":
        matches = lookup_terms(query, top_n=3)
        tool_calls.append({"tool": "dictionary_lookup", "count": len(matches)})
        if matches:
            top = matches[0]
            formula = top["formula"]
            formula_text = f" Formula: {formula}." if formula else ""
            answer = (
                f"{top['term']}: {top['definition']} "
                f"Business meaning: {top['business_meaning']}.{formula_text}"
            )
            sources = ["data/scm_dictionary.json"]
            confidence = max(confidence, top["score"])
        else:
            answer = "I could not find a definition in the SCM dictionary."

    elif intent == "CALCULATION":
        result = run_calculation(query)
        tool_calls.append({"tool": "calculators"})
        answer = result["answer"]
        confidence = max(confidence, result["confidence"])
        sources = ["calculation"]

    else:
        results = rag_search(query, top_k=4)
        tool_calls.append({"tool": "rag_search", "count": len(results)})
        if results:
            top = results[0]
            answer = _first_sentences(top["text"], max_sentences=2)
            sources = [f"{r['source']}#chunk-{r['chunk_id']}" for r in results]
            confidence = max(confidence, top["score"])
        else:
            answer = "I could not find relevant content in the knowledge base."

    if confidence < CONFIDENCE_THRESHOLD:
        terms = related_terms(query, top_n=5)
        related = ", ".join(terms) if terms else "No close terms found"
        answer = f"{CLARIFICATION_PROMPT} Related terms: {related}."

    payload = {
        "run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intent": intent,
        "tool_calls": tool_calls,
        "sources": sources,
        "confidence": confidence,
        "answer": answer,
        "query": query,
    }
    _log_run(payload)

    return {
        "Answer": answer,
        "Sources": sources,
        "Confidence": round(confidence, 3),
        "Domain": intent,
    }
