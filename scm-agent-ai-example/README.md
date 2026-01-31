# SCM Agent AI Example

Production-style, fully local SCM enterprise agent with RAG, terminology dictionary, intent routing, tool orchestration, structured logging, and evaluation.

## Features
- Local RAG over synthetic SCM knowledge base (TF-IDF cosine similarity)
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
python build_kb.py
python run_scm_agent.py
python eval/eval_scm_agent.py
```

## Example query
```bash
python run_scm_agent.py "What is OTIF and how is it measured?"
```

## Optional seed URL ingestion (PDF/PPTX/DOCX)
If `data/seed_urls.json` contains a list of URLs, `build_kb.py` will fetch each URL, store the raw file in `data/raw_data/`, and extract text from:
- PDF pages (one text file per page)
- PPTX slides (one text file per slide)
- DOCX files (single extracted page)
- HTML (tag-stripped text)

When retrieval hits a chunk from a PDF page or PPTX slide, the agent includes the full page/slide text in the context.
No ingestion occurs if the file is absent or empty.

## Notes
- All data is local and synthetic by default.
- Outputs are logged to `logs/scm_runs.jsonl`.
# SCM Agent AI Example

Production-style, fully local SCM enterprise agent with RAG, terminology dictionary, intent routing, tool orchestration, structured logging, and evaluation.

## Features
- Local RAG over synthetic SCM knowledge base (TF-IDF cosine similarity)
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
python build_kb.py
python run_scm_agent.py "What is OTIF and how is it measured?"
python eval/eval_scm_agent.py
```

## Optional seed URL crawling
If you provide `data/seed_urls.json` with a list of URLs, `build_kb.py` will fetch and add those pages to the knowledge base. No crawling occurs if the file is absent or empty.

## Notes
- All data is local and synthetic by default.
- Outputs are logged to `logs/scm_runs.jsonl`.
