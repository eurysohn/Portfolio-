# Evaluation Plan

## Goals
- Prove RAG is wired end-to-end (index → retrieve → answer).
- Quantify routing correctness and retrieval coverage.
- Provide a reproducible evaluation command for CI/local runs.

## Golden Set Design
### Categories (30+ total)
- Dictionary expansion (acronyms/terms)
- Internal RAG (policy/playbook/logistics)
- Structured data query (KPI lookups)
- Out-of-scope guard

### Schema
- `id`
- `category`
- `question`
- `expected_route` (ordered list)
- `expected_sources_hint` (doc id or tag)
- `expected_answer_keypoints` (3–5 bullets)

## Metrics
- **Route accuracy**: expected_route ⊆ trace.route_taken
- **Retrieval hit**: expected_sources_hint appears in top-k retrieval
- **Answer keypoints**: >=2 expected keypoints present

## Pass/Fail Criteria
- Route accuracy ≥ 0.85
- Retrieval hit ≥ 0.80
- Keypoint match ≥ 0.70

## How to Run
```bash
python scripts/build_rag_index.py
python scripts/eval_golden_set.py
```

## Reporting
- Summary: pass count / total
- Failure list with route/retrieval/keypoint diagnostics
