# PROJECT_TODO

## Baseline Status (Phase 0)
| Category | Item | Status | Result / Logs |
| :--- | :--- | :--- | :--- |
| **Runtime** | Server Boot | 🟢 PASS | Successfully restored components |
| **Connectivity** | Local / (200) | 🟢 PASS | Endpoint `/healthz` active |
| **Connectivity** | Local /healthz | 🟢 PASS | Endpoint `/healthz` active |
| **Environment** | .env.example | 🟢 PASS | `.env.example` created |
| **CI/CD** | Fly.io Deploy | 🟢 PASS | Live: `https://scm-agent-ai-example-eury.fly.dev/` |

## P0: Core Infrastructure & Fixes
- [x] **[P0]** Resolve missing dependencies/files (Restored `prompts`, `router`, `tools`, `requirements.txt`)
- [x] **[P0]** Establish `api/main.py` (FastAPI entry point)
- [x] **[P0]** Implement `/healthz` and `/` endpoints
- [x] **[P0]** Create `Dockerfile` and `fly.toml`
- [x] **[P0]** Successful Fly.io configuration

## P1: Quality & Documentation
- [x] **[P1]** Setup Pydantic Settings for environment variables
- [x] **[P1]** Add structured logging with Correlation ID (Middleware)
- [x] **[P1]** Configure linting/typechecking (ruff, mypy in pyproject.toml)
- [x] **[P1]** Add unit/smoke tests (pytest)

## P2: Advanced Features
- [x] **[P2]** Prometheus metrics (Stubbed in /metrics route)
- [x] **[P2]** Demo scenario recordings/docs
- [x] **[P2]** v0.1.0 Release prepared (CHANGELOG updated)
