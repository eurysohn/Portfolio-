# SCM Agent AI Example

Production-style, fully local SCM enterprise agent with RAG, terminology dictionary, intent routing, tool orchestration, structured logging, and evaluation.

## Features
- Supply/Demand RAG over processed source documents (TF-IDF cosine similarity)
- SCM terminology dictionary with synonym mapping and fuzzy lookup
- Intent router across SCM domains
- Tool orchestration (RAG + dictionary + calculators)
- Structured JSONL logging
- Golden-set evaluation
- CLI runner

## Requirements
- Python 3.10+

## Setup
```bash
pip install -r requirements.txt
python download_raw.py
python process_data.py
python build_process_rag.py
python run_scm_agent.py "What is OTIF and how is it measured?"
python eval/eval_scm_agent.py
```

## Example query
```bash
python run_scm_agent.py "What is OTIF and how is it measured?"
```

## Raw data download
If any of the URL list files are present (`data/seed_urls.json`, `data/url_list.json`,
`data/url_list_supply.json`, `data/url_list_demand.json`), `download_raw.py` fetches
each URL and stores the original file in `data/raw_data/`.

## Process data (txt)
`process_data.py` converts files in `data/raw_data/` into plain-text documents in
`data/process_data/`.
- `pptx`: Gemini OCR (set `GEMINI_API_KEY`, optional `GEMINI_MODEL`)
- `pdf/docx/html/txt`: local text extraction/cleanup

## Build supply/demand RAG
`build_process_rag.py` builds two vector indexes from `data/process_data/`:
- Supply index: `storage/vector_db_supply/index.pkl`
- Demand index: `storage/vector_db_demand/index.pkl`

The agent routes queries to supply/demand RAG when supply/demand keywords are detected.

## Notes
- Outputs are logged to `logs/scm_runs.jsonl`.

## Repository structure
```
scm-agent-ai-example/
  README.md
  requirements.txt
  download_raw.py
  process_data.py
  build_process_rag.py
  run_scm_agent.py
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
    url_list.json
    url_list_supply.json
    url_list_demand.json
    raw_data/
    process_data/
    build_synthetic_docs.py
    scm_dictionary.json
    scm_golden_set.json
  storage/
    vector_db/
    vector_db_supply/
    vector_db_demand/
  logs/
    scm_runs.jsonl
  eval/
    eval_scm_agent.py
  tests/
    test_router.py
    test_dictionary.py
```
- Outputs are logged to `logs/scm_runs.jsonl`.
