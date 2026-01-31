import json
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from agent.prompts import ANSWER_TEMPLATE, SYSTEM_PROMPT
from agent.router import route
from tools.calculators import economic_order_quantity, fill_rate, otif, reorder_point, safety_stock
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


def run_agent(query: str, confidence_threshold: float = 0.55, top_k: int = 3) -> Dict:
    dict_results, related_terms = lookup(query)
    routing = route(query, related_terms)
    intent = routing["intent"]
    confidence = routing["confidence"]
    sources = []
    answer = ""
    tool_calls = []
    handled = False

    text = query.lower()
    scm_keywords = [
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
    ]
    if not any(k in text for k in scm_keywords):
        answer = (
            "I can only answer SCM-related questions. "
            "Please ask about supply chain, demand planning, inventory, or logistics."
        )
        sources = []
        tool_calls.append("scm_guard")
        return {
            "answer": _to_markdown(answer),
            "sources": sources,
            "confidence": confidence,
            "domain": intent,
            "formatted": ANSWER_TEMPLATE.format(
                answer=_to_markdown(answer),
                sources=_format_sources(sources),
                confidence=confidence,
                domain=intent,
            ),
        }
    if "수요예측" in text or "demand forecast" in text or "forecast" in text:
        answer = (
            "## Demand forecasting methods (practical)\n"
            "- **Qualitative**: sales/marketing input, Delphi, scenario planning to form an initial baseline.\n"
            "- **Quantitative**: statistical models based on historical sales data.\n"
            "\n"
            "## Key formulas (examples)\n"
            "- **Simple Moving Average (SMA)**: D̂(t+1) = (D_t + D_{t-1} + ... + D_{t-n+1}) / n\n"
            "- **Simple Exponential Smoothing (SES)**: D̂(t+1) = α·D_t + (1-α)·D̂_t\n"
            "- **MAPE**: MAPE = (1/n) · Σ |(D_t - D̂_t) / D_t| × 100\n"
            "\n"
            "## Quick examples\n"
            "- If the last 3 months are 100, 120, 110, then SMA(3) = 110.\n"
            "- If α=0.3, D_t=120, D̂_t=110, then SES forecast = 113.\n"
            "\n"
            "## Practical checklist\n"
            "- Separate **seasonality/promotions** as explicit model inputs.\n"
            "- Monitor accuracy with **MAPE, WAPE, Bias**.\n"
            "- Use **ABC segmentation**: A-items get advanced models, C-items use simpler models.\n"
            "\n"
            "## Case examples (illustrative)\n"
            "- Company A: inventory surplus → ABC + SES → **12% inventory turnover improvement**.\n"
            "- Company B: promo spike → add promo drivers → **18% stockout reduction**.\n"
        )
        sources = [
            {
                "chunk_id": "built_in_definition",
                "source": "built_in_definition",
                "score": 1.0,
                "text": "수요예측 방법론",
                "page_text": "",
            }
        ]
        tool_calls.append("definition_fallback")
        intent = "PLANNING"
        handled = True
    elif "안전재고" in text or "safety stock" in text:
        answer = (
            "Safety stock is buffer inventory used to absorb demand variability and lead-time uncertainty. "
            "A common formula is Safety Stock = Z × σd × √L, where Z is the service-level z-score, "
            "σd is the daily demand standard deviation, and L is lead time (days)."
        )
        sources = [
            {
                "chunk_id": "built_in_definition",
                "source": "built_in_definition",
                "score": 1.0,
                "text": "안전재고 공식",
                "page_text": "",
            }
        ]
        tool_calls.append("definition_fallback")
        intent = "INVENTORY"
        handled = True

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
        focused = _select_relevant_sentences(query, context, max_sentences=3)
        if focused:
            answer = focused
        else:
            summary = _summarize_context(context, max_sentences=3)
            answer = summary if summary else "No relevant information found in sources."
        tool_calls.append("rag_search")

        if answer == "No relevant information found in sources." or _scores_too_low(sources):
            web_results = web_search(query, max_results=3)
            if web_results:
                answer = " ".join([r["snippet"] for r in web_results if r["snippet"]])
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
                tool_calls.append("web_search")

    if confidence < confidence_threshold:
        related = ", ".join(related_terms[:5]) if related_terms else "No related terms found"
        answer = (
            "I want to be precise. Can you clarify your request? "
            f"Related terms: {related}"
        )
        sources = []

    answer = _to_markdown(answer)

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
