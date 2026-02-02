from agent.engine import run_agent
from tools.rag_index import build_index


def test_rag_retrieves_internal_marker():
    build_index()
    result = run_agent("What is ZETA-LOCK-42 used for?", top_k=3)
    sources = [s["source"] for s in result.get("sources", [])]
    assert any("scm_policy.md" in source for source in sources)
    assert "Workflow Trace" in result.get("formatted", "")
