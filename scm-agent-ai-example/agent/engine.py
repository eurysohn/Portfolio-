import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agent.prompts import ANSWER_TEMPLATE
from agent.router import route
from app.trace_schema import RetrievalHit, WorkflowTrace
from config import settings
from tools.calculators import economic_order_quantity, fill_rate, otif, reorder_point, safety_stock
from tools.data_query import query_kpi
from tools.dictionary_lookup import lookup
from tools.rag_search import search
from tools.web_search import web_search

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_PATH = BASE_DIR / "logs" / "scm_runs.jsonl"
STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "for",
    "in",
    "on",
    "with",
    "is",
    "are",
    "was",
    "were",
    "be",
    "this",
    "that",
    "these",
    "those",
    "it",
    "as",
    "at",
    "by",
    "from",
    "what",
    "how",
    "why",
    "when",
    "which",
    "who",
    "where",
    "i",
    "we",
    "you",
    "your",
    "our",
    "and/or",
    "about",
    "into",
    "than",
    "also",
    "can",
    "could",
    "should",
    "would",
    "may",
    "might",
    "do",
    "does",
    "did",
    "done",
    "안",
    "이",
    "그",
    "저",
    "것",
    "수",
    "하는",
    "하기",
    "되",
    "된다",
    "될",
    "좀",
    "좀더",
    "방법",
    "어떻게",
    "무엇",
    "뭐",
    "설명",
    "알려줘",
    "알려",
    "해주세요",
    "해줘",
}


SCM_KEYWORDS = {
    "scm",
    "supply chain",
    "supply",
    "supplier",
    "procurement",
    "logistics",
    "warehouse",
    "inventory",
    "demand",
    "forecast",
    "s&op",
    "otif",
    "fill rate",
    "reorder point",
    "safety stock",
    "수요",
    "공급",
    "공급망",
    "조달",
    "물류",
    "창고",
    "재고",
    "예측",
}


def is_scm_question(query: str) -> bool:
    text = query.lower()
    out_of_scope = ["weather", "poem", "game", "sports", "movie", "celebrity"]
    if any(keyword in text for keyword in out_of_scope):
        return False
    dict_results, _ = lookup(query)
    return any(keyword in text for keyword in SCM_KEYWORDS) or bool(dict_results)


def expand_with_dictionary(query: str) -> Tuple[str, List[str]]:
    dict_results, related_terms = lookup(query)
    if not dict_results:
        return query, []
    expansions = []
    for entry in dict_results:
        expansions.append(entry["term"])
        expansions.append(entry["definition"])
        expansions.append(entry["business_meaning"])
        if entry.get("formula"):
            expansions.append(f"formula: {entry['formula']}")
    expanded = f"{query}\n\nDictionary expansions:\n" + "\n".join(expansions)
    return expanded, related_terms


def retrieve_internal_knowledge(expanded_question: str, top_k: int) -> List[Dict]:
    return search(expanded_question, top_k=top_k)


def maybe_run_data_query(query: str) -> Optional[Dict]:
    return query_kpi(query)


def maybe_run_web_search(query: str) -> List[Dict]:
    return web_search(query, max_results=3)


def _source_url(source_id: str) -> str:
    if source_id.startswith("http"):
        return source_id
    base = settings.DOCS_BASE_URL.rstrip("/")
    return f"{base}/{source_id}.md"


def _sources_markdown(source_ids: List[str]) -> str:
    unique = []
    for source_id in source_ids:
        if source_id not in unique:
            unique.append(source_id)
    if not unique:
        return "- None"
    return "\n".join(f"- {_source_url(source_id)}" for source_id in unique)


def _to_bullets(text: str) -> List[str]:
    chunks = [c.strip() for c in re.split(r"[\n\.]", text) if c.strip()]
    return [f"- {c}" for c in chunks]


def _build_rag_answer(query: str, context: str, detailed: bool, source_ids: List[str]) -> str:
    focused = _select_relevant_sentences(query, context, max_sentences=5 if detailed else 3)
    summary = focused or _summarize_context(context, max_sentences=5 if detailed else 3)
    if not summary:
        return "No relevant information found in sources."

    key_points = _select_relevant_sentences(query, context, max_sentences=6 if detailed else 4)
    key_bullets = _to_bullets(key_points or summary)

    sections = []
    sections.append("## 핵심 내용\n" + "\n".join(key_bullets))
    sections.append("Sources:\n" + _sources_markdown(source_ids))

    if detailed:
        detail_text = summary
        sections.append("\n## 세부 설명\n" + detail_text)
        sections.append("Sources:\n" + _sources_markdown(source_ids))

    return "\n\n".join(sections)

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


def _detect_rag_domain(query: str) -> Optional[str]:
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


def _select_relevant_sentences(query: str, context: str, max_sentences: int = 3) -> str:
    clean = re.sub(r"\s+", " ", context).strip()
    if not clean:
        return ""
    query_tokens = {
        token
        for token in re.split(r"[^a-zA-Z0-9가-힣]+", query.lower())
        if token and token not in STOPWORDS
    }
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    scored = []
    for sentence in sentences:
        tokens = {
            token
            for token in re.split(r"[^a-zA-Z0-9가-힣]+", sentence.lower())
            if token and token not in STOPWORDS
        }
        if not tokens:
            continue
        score = len(query_tokens & tokens)
        if score > 0:
            scored.append((score, sentence))
    if not scored:
        return ""
    scored.sort(key=lambda item: item[0], reverse=True)
    picked = [sentence for _, sentence in scored[:max_sentences]]
    return " ".join(picked).strip()


def _scores_too_low(sources: List[Dict], threshold: float = 0.01) -> bool:
    if not sources:
        return True
    return all(s.get("score", 0.0) <= threshold for s in sources)


def _to_markdown(answer: str, max_bullets: int = 5) -> str:
    text = answer.strip()
    if not text:
        return text
    if any(marker in text for marker in ("##", "\n- ", "\n* ")):
        return text

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return text

    method_keywords = [
        "방법",
        "기법",
        "모델",
        "정성",
        "정량",
        "시계열",
        "회귀",
        "인과",
        "머신러닝",
        "시나리오",
        "지수평활",
        "이동평균",
        "계절성",
    ]
    method_sentences = [s for s in sentences if any(k in s for k in method_keywords)]
    bullets = method_sentences[:max_bullets] if method_sentences else sentences[:3]

    # Drop dangling numeric bullet like "1."
    bullets = [b for b in bullets if b not in {"1.", "2.", "3."}]

    if not bullets:
        return text

    formatted = "\n".join(f"- {b}" for b in bullets)
    return formatted


def run_agent(query: str, confidence_threshold: float = 0.55, top_k: int = 3, api_key: Optional[str] = None) -> Dict:
    trace = WorkflowTrace(input=query, normalized_input=query.strip().lower())
    routing = route(query, [])
    intent = routing["intent"]
    confidence = routing["confidence"]
    sources: List[Dict[str, Any]] = []
    answer = ""
    tool_calls: List[str] = []

    if not is_scm_question(query):
        trace.add_route("scm_check")
        trace.decisions.append("Rejected: non-SCM query.")
        answer = (
            "I can only answer SCM-related questions. "
            "Please ask about supply chain, demand planning, inventory, or logistics."
        )
        formatted = ANSWER_TEMPLATE.format(
            answer=_to_markdown(answer),
            sources=_format_sources([]),
            confidence=confidence,
            domain="OUT_OF_SCOPE",
        )
        trace.output = answer
        payload = {
            "run_id": str(uuid.uuid4()),
            "query": query,
            "intent": "OUT_OF_SCOPE",
            "tool_calls": tool_calls,
            "sources": [],
            "confidence": confidence,
            "answer": answer,
            "trace": trace.model_dump(),
        }
        _log_run(payload)
        return {
            "answer": _to_markdown(answer),
            "sources": [],
            "confidence": confidence,
            "domain": "OUT_OF_SCOPE",
            "formatted": formatted,
            "trace": trace.model_dump(),
            "trace_summary": trace.summary(),
        }

    trace.add_route("scm_check")

    expanded_question, dictionary_hits = expand_with_dictionary(query)
    if dictionary_hits:
        trace.add_route("dictionary_expand")
        trace.dictionary_hits = dictionary_hits
        trace.decisions.append("Expanded query using dictionary terms.")

    try:
        sources = retrieve_internal_knowledge(expanded_question, top_k=top_k)
        trace.add_route("rag_answer")
    except FileNotFoundError:
        sources = []
        trace.decisions.append("RAG index missing; run build_rag_index.py.")

    retrieval_hits = []
    for item in sources:
        retrieval_hits.append(
            RetrievalHit(
                source_id=item.get("source", "unknown"),
                chunk_id=item.get("chunk_id", "unknown"),
                score=float(item.get("score", 0.0)),
                snippet=item.get("text", "")[:160],
            )
        )
    trace.retrieval_hits = retrieval_hits
    trace.citations = [hit.source_id for hit in retrieval_hits]

    data_result = maybe_run_data_query(query)
    if data_result:
        trace.add_route("data_query")
        trace.add_tool("data_query")
        trace.decisions.append("Structured KPI lookup matched query.")

    context_blocks: List[str] = []
    for s in sources:
        if s.get("page_text"):
            context_blocks.append(s["page_text"])
        else:
            context_blocks.append(s["text"])
    context = "\n\n".join(context_blocks)[:2000]
    detailed = any(token in query.lower() for token in ["detail", "detailed", "explain", "how"])
    answer = _build_rag_answer(query, context, detailed=detailed, source_ids=trace.citations)

    if data_result:
        structured = json.dumps(data_result, ensure_ascii=True)
        answer = f"Structured data:\n{structured}\n\nRAG context:\n{answer}"

    if not data_result and (answer == "No relevant information found in sources." or _scores_too_low(sources)):
        trace.decisions.append("RAG confidence low; using web fallback.")
        web_results = maybe_run_web_search(query)
        if web_results:
            snippets: List[str] = []
            for result in web_results:
                snippet = result.get("snippet")
                if isinstance(snippet, str) and snippet:
                    snippets.append(snippet)
            if snippets:
                answer = " ".join(snippets)
            sources = [
                {
                    "chunk_id": f"web:{idx}",
                    "source": r["url"],
                    "score": r.get("score", 1.0),
                    "text": r.get("title", "Web result"),
                    "page_text": r.get("snippet", ""),
                }
                for idx, r in enumerate(web_results, start=1)
            ]
            trace.citations = [item["source"] for item in sources]
            trace.add_route("web_search")
            trace.add_tool("web_search")

    if confidence < confidence_threshold and answer == "No relevant information found in sources." and not data_result:
        related = ", ".join(dictionary_hits[:5]) if dictionary_hits else "No related terms found"
        answer = (
            "I want to be precise. Can you clarify your request? "
            f"Related terms: {related}"
        )
        sources = []
        trace.decisions.append("Low confidence; requested clarification.")

    answer = _to_markdown(answer)
    trace.output = answer

    formatted = ANSWER_TEMPLATE.format(
        answer=answer,
        sources=_format_sources(sources),
        confidence=confidence,
        domain=intent,
    )
    formatted = f"{formatted}\n\n---\n{trace.summary()}"

    payload = {
        "run_id": str(uuid.uuid4()),
        "query": query,
        "intent": intent,
        "tool_calls": tool_calls,
        "sources": [s["source"] for s in sources],
        "confidence": confidence,
        "answer": answer,
        "trace": trace.model_dump(),
    }
    _log_run(payload)

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "domain": intent,
        "formatted": formatted,
        "trace": trace.model_dump(),
        "trace_summary": trace.summary(),
    }
