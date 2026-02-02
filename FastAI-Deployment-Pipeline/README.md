# FastAPI Deployment Pipeline

[![CI Pipeline](https://github.com/eurysohn/Portfolio-/actions/workflows/ci.yml/badge.svg)](https://github.com/eurysohn/Portfolio-/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Production-ready FastAPI deployment pipeline demonstrating DevOps best practices.**

This repository serves as a reference implementation for building, testing, and deploying FastAPI applications with enterprise-grade CI/CD pipelines, observability, and security practices.

---

## Architecture Overview

```mermaid
graph TB
    subgraph CICD[CI/CD Pipeline - GitHub Actions]
        direction LR
        A[Pull Request] --> B[Lint]
        B --> C[Security Scan]
        C --> D[Test]
        D --> E[Build Docker]
        E --> F[Push to GHCR]
        F --> G[Deploy]
    end
    
    subgraph Stack[Application Stack - Docker Compose]
        direction TB
        API[FastAPI API<br/>Port 8000]
        REDIS[(Redis Cache<br/>Port 6379)]
        PROM[Prometheus<br/>Port 9090]
        GRAF[Grafana<br/>Port 3000]
        
        API -->|cache| REDIS
        API -->|metrics| PROM
        PROM -->|data source| GRAF
    end
    
    CICD --> Stack
```

### System Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **API Server** | REST API with health checks & metrics | FastAPI, Uvicorn |
| **Cache Layer** | Response caching, session store | Redis |
| **Metrics** | Time-series metrics collection | Prometheus |
| **Dashboard** | Visualization & alerting | Grafana |
| **CI/CD** | Automated testing & deployment | GitHub Actions |

---

## CI/CD Pipeline

```mermaid
flowchart LR
    subgraph Triggers
        PR[Pull Request]
        PUSH[Push to main]
        TAG[Version Tag]
    end
    
    subgraph CI[Continuous Integration]
        LINT[Lint & Format<br/>Ruff, Black, MyPy]
        SEC[Security Scan<br/>Bandit, Safety, Trivy]
        TEST[Unit Tests<br/>Pytest 70%+ Coverage]
        BUILD[Docker Build<br/>Multi-stage]
    end
    
    subgraph CD[Continuous Deployment]
        PUSH_REG[Push to GHCR]
        DEPLOY[Deploy to Environment]
    end
    
    PR --> LINT
    PUSH --> LINT
    TAG --> LINT
    
    LINT --> SEC --> TEST --> BUILD
    BUILD --> PUSH_REG --> DEPLOY
```

### Pipeline Stages

| Stage | Tools | Description |
|-------|-------|-------------|
| **Lint** | Ruff, Black, MyPy | Code quality & type checking |
| **Security** | Bandit, Safety, Trivy | SAST & dependency scanning |
| **Test** | Pytest | Unit tests with 70% coverage threshold |
| **Build** | Docker | Multi-stage production image |
| **Push** | GHCR | GitHub Container Registry |
| **Deploy** | Mock | Deployment simulation |

---

## Project Structure

```
FastAI-Deployment-Pipeline/
│
├── app/                          # Application source code
│   ├── api/                      # API endpoints
│   │   ├── health.py             # /healthz, /readyz endpoints
│   │   ├── metrics.py            # /metrics (Prometheus)
│   │   └── v1/items.py           # CRUD operations
│   ├── core/                     # Core modules
│   │   ├── config.py             # Pydantic settings
│   │   └── logging.py            # Structured logging
│   ├── middleware/               # Request tracing
│   ├── services/cache.py         # Redis service
│   └── main.py                   # App entry point
│
├── tests/                        # Test suite (pytest)
├── .github/workflows/            # CI/CD pipelines
├── monitoring/                   # Prometheus & Grafana
├── load_tests/                   # Locust performance tests
├── docs/                         # ADRs & Runbook
│
├── Dockerfile                    # Multi-stage build
├── docker-compose.yml            # Full stack
└── Makefile                      # Developer commands
```

---

## Quick Start

### Prerequisites

- **Docker & Docker Compose** - For running the full stack
- **Python 3.9+** - For local development

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/eurysohn/Portfolio-.git
cd Portfolio-/FastAI-Deployment-Pipeline

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Stop services
docker-compose down
```

**Services available after startup:**

| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | FastAPI application (`/docs` for Swagger UI) |
| Prometheus | 9090 | Metrics dashboard |
| Grafana | 3000 | Visualization (login: admin/admin) |
| Redis | 6379 | Cache (internal) |

### Option 2: Local Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Start the API
uvicorn app.main:app --reload --port 8000
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/healthz` | GET | Liveness probe (Kubernetes) |
| `/readyz` | GET | Readiness probe (Kubernetes) |
| `/health` | GET | Detailed health check |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | Swagger UI documentation |
| `/api/v1/items` | GET | List items (paginated) |
| `/api/v1/items` | POST | Create item |
| `/api/v1/items/{id}` | GET | Get item by ID |
| `/api/v1/items/{id}` | PUT | Update item |
| `/api/v1/items/{id}` | DELETE | Delete item |

---

## Key Features

### Observability
- **Structured JSON Logging** - ELK/CloudWatch compatible
- **Request ID Tracing** - Distributed tracing support
- **Prometheus Metrics** - Request rate, latency, errors
- **Grafana Dashboards** - Pre-configured visualizations

### Security
- **Non-root Container** - Principle of least privilege
- **SAST Scanning** - Static analysis with Bandit
- **Dependency Audit** - Vulnerability scanning with Safety
- **Container Scanning** - Trivy integration
- **Secret Detection** - Gitleaks in CI

### Developer Experience
- **Makefile** - Common commands (`make test`, `make run`)
- **Pre-commit Hooks** - Automatic code quality checks
- **Hot Reload** - Fast development iteration
- **Comprehensive Tests** - 80%+ code coverage

---

## Available Commands

```bash
make help          # Show all available commands
make dev           # Install development dependencies
make test          # Run tests with coverage
make lint          # Run linters (ruff, mypy)
make format        # Auto-format code
make security      # Run security checks
make build         # Build Docker image
make docker-up     # Start all services
make docker-down   # Stop all services
make ci            # Run full CI pipeline locally
```

---

## DevOps Best Practices Demonstrated

| Practice | Implementation |
|----------|----------------|
| **Infrastructure as Code** | Dockerfile, docker-compose.yml |
| **CI/CD Automation** | GitHub Actions workflows |
| **Shift-Left Security** | Security scanning in CI |
| **Observability** | Metrics, logging, health checks |
| **GitOps Ready** | Container images, version tags |
| **Documentation** | ADRs, runbooks, API docs |

---

## Documentation

- [Architecture Decision Records](docs/architecture/) - Design decisions
- [Operations Runbook](docs/runbook.md) - Incident response guide
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Security Policy](SECURITY.md) - Vulnerability reporting

---

## Tech Stack

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat&logo=grafana&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=github-actions&logoColor=white)

---

## License

MIT License - see [LICENSE](LICENSE) for details.
