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
uvicorn api.main:app --port 8080 --reload
```

### 3. Test Endpoints
- **Health Check**: `curl http://localhost:8080/healthz`
- **Query Agent**:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is OTIF?", "top_k": 3}'
```

## 🚢 Fly.io Deployment
1. **Login & Launch**: `fly launch` (Uses existing `fly.toml`)
2. **Set Secrets**: `fly secrets set OPENAI_API_KEY=sk-...`
3. **Deploy**: `fly deploy`

## 📊 Demo Scenarios
1. **SCM Definition**: "What is EOQ and how is it measured?" -> Returns business definition + formula.
2. **Real-time Calculation**: "Calculate OTIF for 90% on-time and 95% in-full." -> Returns `85.5%`.
3. **Knowledge Search**: "How to improve demand forecasting?" -> Returns RAG-based insights.

## 🏗️ Advanced Docs
- [ARCHITECTURE.md](ARCHITECTURE.md) - Design patterns & data flow.
- [CONTRIBUTING.md](CONTRIBUTING.md) - Local dev & PR guidelines.
- [CHANGELOG.md](CHANGELOG.md) - Version history.
