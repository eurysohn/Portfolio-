## SCM Agent AI Example

A fully local, production-style SCM enterprise agent with:
- RAG over a local SCM knowledge base
- SCM terminology dictionary with synonym mapping
- Intent routing across SCM domains
- Tool orchestration and structured jsonl logging
- Golden-set evaluation
- CLI runner

### Quick start

```bash
pip install -r requirements.txt
python build_kb.py
python run_scm_agent.py --query "What is OTIF and how is it measured?"
python eval/eval_scm_agent.py
```

### What gets generated
- `data/enterprise_knowledge/`: synthetic SCM docs (idempotent)
- `storage/vector_db/`: TF-IDF vector index (and optional sentence-transformers embeddings)
- `logs/scm_runs.jsonl`: structured run logs

### CLI usage

```bash
python run_scm_agent.py --query "How do I calculate reorder point?"
python run_scm_agent.py
```

If `--query` is omitted, the runner opens an interactive prompt.

### Optional crawling

If `data/seed_urls.json` contains seed URLs, `build_kb.py` will fetch those pages
and add their text to the knowledge base. No broad crawling is performed.

### Repository structure

```
scm-agent-ai-example/
  README.md
  requirements.txt
  run_scm_agent.py
  build_kb.py
  agent/
    __init__.py
    engine.py
    router.py
    prompts.py
  tools/
    __init__.py
    rag_search.py
    dictionary_lookup.py
    calculators.py
  data/
    seed_urls.json
    build_synthetic_docs.py
    scm_dictionary.json
    scm_golden_set.json
    enterprise_knowledge/
  storage/
    vector_db/
  logs/
    scm_runs.jsonl
  eval/
    eval_scm_agent.py
  tests/
    test_router.py
    test_dictionary.py
```
