# Changelog

## [v0.1.0] - 2026-02-02
### Added
- Product-grade FastAPI service.
- Multi-stage Dockerfile and Fly.io configuration.
- Comprehensive test suite (Unit + Smoke).
- GitHub Actions CI for linting and testing.
- SCM metric calculators (EOQ, OTIF, etc.).
- Robust documentation (ARCHITECTURE, CONTRIBUTING).
- Correlation ID middleware for distributed tracing.
- Minimal `/metrics` endpoint for Prometheus scraping.
- Health payload now includes `git_sha` for build traceability.
- Real RAG indexing + retrieval with internal knowledge base.
- Workflow trace schema with route/tool decisions in responses.
- Synthetic golden set + evaluation script.
