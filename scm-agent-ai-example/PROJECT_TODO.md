# PROJECT_TODO

## Baseline Status (Phase 0)
| Category | Item | Status | Result / Logs |
| :--- | :--- | :--- | :--- |
| **Runtime** | Server Boot | 🔴 FAIL | `NameError: name 'Optional' is not defined` in `api/main.py` |
| **Connectivity** | Local / (200) | ⚪️ NOT RUN | Blocked by server boot failure |
| **Connectivity** | Local /healthz | ⚪️ NOT RUN | Blocked by server boot failure |
| **Environment** | .env.example | 🟢 PASS | `cp .env.example .env` succeeded |
| **Dependencies** | pip install | 🟡 WARN | Installed, but resolver conflict with `enterprise-text-to-sql-agent` in global env |
| **CI/CD** | Fly.io Deploy | ⚪️ NOT RUN | Not attempted in Phase 0 baseline |
| **RAG** | Indexing/Search Wiring | 🟢 PASS | `scripts/build_rag_index.py` builds index; `tools.rag_search` loads real index |

### Reproduction Log (Phase 0)
- `cp .env.example .env`
- `python3 -m pip install -r requirements.txt`
- `python3 -m uvicorn api.main:app --port 8080`
- Error:
  - `NameError: name 'Optional' is not defined` at `api/main.py:19`

### RAG Baseline Evidence (Phase 0)
**Before**
- Runtime call path:
  - `api/main.py` → `agent/engine.py:387` → `tools/rag_search.search`
- Evidence of mock retrieval:
  - `tools/rag_search.search` returns hardcoded data (`# Mock RAG search results`)
- Indexing scripts/files:
  - Not found (no `build_index`, vector DB libs, or index artifacts)

**After**
- Index build:
  - `python scripts/build_rag_index.py` → `Indexed 8 chunks.`
- Retrieval proof:
  - Query: `What is ZETA-LOCK-42 used for?`
  - Trace includes `rag_answer` and source `scm_policy`

## Backlog & Status
| Priority | Item | Status | Acceptance Criteria | Owner | Links |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P0** | RAG indexing + retrieval wiring | ✅ DONE | Index build + runtime retrieval with trace proof | assistant | `tools/rag_index.py`, `tools/rag_search.py` |
| **P0** | RAG proof experiment | ✅ DONE | Query retrieves internal-only marker with trace | assistant | `README.md` |
| **P0** | Trace schema + response trace | ✅ DONE | `trace` + `trace_summary` in API responses | assistant | `app/trace_schema.py`, `agent/engine.py` |
| **P1** | Golden set + eval script | ✅ DONE | `eval_golden_set.py` reports metrics | assistant | `data/golden_set_synth.jsonl`, `scripts/eval_golden_set.py` |
| **P1** | Agentic workflow (fallback decisions) | ✅ DONE | Trace shows RAG → data/web decisions | assistant | `agent/engine.py` |
| **P1** | Docs for RAG/Eval | ✅ DONE | README + EVAL_PLAN updated | assistant | `README.md`, `EVAL_PLAN.md` |
| **P2** | Release tag v0.1.0 | ⬜️ TODO | Git tag created on release commit | you | `CHANGELOG.md` |

## P0: Core Infrastructure & Fixes
- [x] **[P0]** Resolve missing dependencies/files (Restored `prompts`, `router`, `tools`, `requirements.txt`)
- [x] **[P0]** Establish `api/main.py` (FastAPI entry point)
- [x] **[P0]** Implement `/healthz` and `/` endpoints
- [x] **[P0]** Create `Dockerfile` and `fly.toml`
- [x] **[P0]** Successful Fly.io configuration

### P0 Fix Log
- **Symptom**: API server failed to start (`NameError: Optional` in `api/main.py`).
- **Root Cause**: Missing `Optional` import and absent observability endpoints.
- **Fix**: Added typing imports, request logging, minimal `/metrics`, and health payload fields.
- **Verification**: `python3 -m pytest` (all tests pass).
- **Regression Guard**: Added `/metrics` test in `tests/test_api.py`.
- **Symptom**: Potential port mismatch between Fly `internal_port` and runtime bind if `PORT` changes.
- **Root Cause**: Docker CMD pinned to `--port 8080` regardless of `PORT`.
- **Fix**: Use `PORT` env in Docker CMD.
- **Verification**: Dockerfile updated; runtime port now follows `PORT`.
- **Regression Guard**: Fly `internal_port` and `.env.example` keep `PORT=8080`.
- **Symptom**: CI typecheck failed (`mypy` module resolution and typing errors).
- **Root Cause**: `api` not marked as a package; loose typing in agent pipeline.
- **Fix**: Added `api/__init__.py` and type annotations in `agent` modules.
- **Verification**: `python3 -m ruff check .` + `python3 -m mypy .` + `python3 -m pytest`.
- **Regression Guard**: CI continues to run lint + mypy + pytest.
- **Symptom**: Risk of committing secrets/log artifacts (`.env`, `logs/`).
- **Root Cause**: Missing root `.gitignore`.
- **Fix**: Added `.gitignore` to exclude secrets, caches, and build artifacts.
- **Verification**: `.env` and `logs/` now ignored by git.
- **Regression Guard**: Keep `.env.example` as the only tracked env template.
- **Symptom**: UI turns blank after submitting a question.
- **Root Cause**: Frontend assumed response shape and could crash on unexpected payloads or missing `/api` routes.
- **Fix**: Hardened frontend response parsing and added `/api/*` + `/health` aliases in FastAPI.
- **Verification**: Manual UI flow should no longer crash on malformed responses.
- **Regression Guard**: Added defensive parsing + stable aliases.
- **Symptom**: RAG pipeline was a mock and not provable end-to-end.
- **Root Cause**: `tools/rag_search` returned hardcoded results with no index.
- **Fix**: Added real TF-IDF index build + retrieval + trace schema.
- **Verification**: `python scripts/build_rag_index.py` and `python scripts/eval_golden_set.py` (30/30).
- **Regression Guard**: `tests/test_rag_pipeline.py` asserts internal marker retrieval.

### Fly Deploy Log
- **Command**: `fly deploy`
- **Result**: ✅ Deployed to `https://scm-agent-ai-example-eury.fly.dev/`
- **Checks**:
  - `GET /healthz` → 200
  - `GET /metrics` → 200
  - `POST /query` → 200

## P1: Quality & Documentation
- [x] **[P1]** Setup Pydantic Settings for environment variables
- [x] **[P1]** Add structured logging with Correlation ID (Middleware)
- [x] **[P1]** Configure linting/typechecking (ruff, mypy in pyproject.toml)
- [x] **[P1]** Add unit/smoke tests (pytest)

## P2: Advanced Features
- [x] **[P2]** Prometheus metrics (Stubbed in /metrics route)
- [x] **[P2]** Demo scenario recordings/docs
- [x] **[P2]** v0.1.0 Release prepared (CHANGELOG updated)
