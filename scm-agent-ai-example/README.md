# SCM Agent API (Product-Grade)

[![CI](https://github.com/eurysohn/Portfolio-/actions/workflows/ci.yml/badge.svg)](https://github.com/eurysohn/Portfolio-/actions/workflows/ci.yml)

A production-ready FastAPI service for Supply Chain Management (SCM) intelligence. Features include intent routing, SCM metric calculators, RAG (Retrieval-Augmented Generation), and seamless Fly.io deployment.

## 🚀 10-Second Summary
- **What**: Intelligent SCM assistant via REST API.
- **Why**: Demonstrates enterprise-grade FastAPI patterns, structured logging, CI/CD, and AI agent orchestration.
- **Tech**: FastAPI, Pydantic v2, Docker (Multi-stage), Fly.io, GitHub Actions, Ruff/Pytest.

## 🛠️ 10-Minute Quickstart (Local)

### 1. Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Run API
```bash
python -m uvicorn api.main:app --port 8080 --reload
```

### 3. Test Endpoints
- **Health Check**: `curl http://localhost:8080/healthz`
- **Metrics**: `curl http://localhost:8080/metrics`
- **Query Agent**:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is OTIF?", "top_k": 3}'
```

## ✅ Quality Gates (CI)
- **Lint**: `python -m ruff check .`
- **Typecheck**: `python -m mypy .`
- **Tests**: `python -m pytest`

## 🔎 RAG Proof (Reproducible)
1. Build the index from internal docs:
```bash
python scripts/build_rag_index.py
```
2. Ask for the internal-only marker:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ZETA-LOCK-42 used for?", "top_k": 3}'
```
3. Inspect the response trace to confirm retrieval from `scm_policy`.

## ✅ Golden Set Evaluation
```bash
python scripts/eval_golden_set.py
```

## 🔧 Environment Variables
- `APP_NAME`: Service name.
- `APP_VERSION`: Release version (e.g., `0.1.0`).
- `ENV`: `local` | `dev` | `staging` | `prod`.
- `PORT`: API port (Fly `internal_port` must match).
- `LOG_LEVEL`: `INFO` by default.
- `GIT_SHA`: Optional commit hash for health reporting.
- `REQUIRE_API_KEY`: Require `OPENAI_API_KEY` for `/query` (default false).
- `OPENAI_API_KEY`: **Secret** (set via `fly secrets set`).

## 🚢 Fly.io Deployment
1. **Login & Launch**: `fly launch` (Uses existing `fly.toml`)
2. **Set Secrets**: `fly secrets set OPENAI_API_KEY=sk-...`
3. **Deploy**: `fly deploy`

## 🌐 Live Demo
- https://scm-agent-ai-example-eury.fly.dev/

## 📊 Demo Scenarios
1. **SCM Definition**: "What is EOQ and how is it measured?" -> Returns business definition + formula.
   - Local: `curl -X POST http://localhost:8080/query -H "Content-Type: application/json" -d '{"query": "What is EOQ and how is it measured?", "top_k": 3}'`
   - Fly: `curl -X POST https://<app-name>.fly.dev/query -H "Content-Type: application/json" -d '{"query": "What is EOQ and how is it measured?", "top_k": 3}'`
2. **Real-time Calculation**: "Calculate OTIF for 90% on-time and 95% in-full." -> Returns `85.5%`.
   - Local: `curl -X POST http://localhost:8080/query -H "Content-Type: application/json" -d '{"query": "Calculate OTIF for 90% on-time and 95% in-full.", "top_k": 3}'`
   - Fly: `curl -X POST https://<app-name>.fly.dev/query -H "Content-Type: application/json" -d '{"query": "Calculate OTIF for 90% on-time and 95% in-full.", "top_k": 3}'`
3. **Knowledge Search**: "How to improve demand forecasting?" -> Returns RAG-based insights.

## 🏗️ Advanced Docs
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design patterns & data flow.
- [CONTRIBUTING.md](CONTRIBUTING.md) - Local dev & PR guidelines.
- [CHANGELOG.md](CHANGELOG.md) - Version history.
