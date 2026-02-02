# fastapi-deployment-pipeline

Production-style FastAPI service for demonstrating containerization, health checks,
metrics, CI-friendly structure, and load testing basics.

## Structure

```
fastapi-deployment-pipeline/
  app/
    __init__.py
    main.py
    metrics.py
  docker/
    Dockerfile
  prometheus/
    prometheus.yml
  docker-compose.yml
  requirements.txt
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export REDIS_HOST=localhost
export REDIS_PORT=6379

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Ensure Redis is running locally (or via `docker compose`).

## Docker Compose

```bash
docker compose up --build
```

Services:
- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin by default)

## Endpoints

```bash
curl -X POST http://localhost:8000/hit
curl http://localhost:8000/stats
curl http://localhost:8000/healthz
curl http://localhost:8000/metrics
```

## Load testing example

```bash
hey -n 1000 -c 20 -m POST http://localhost:8000/hit
```

## CI pipeline

GitHub Actions workflow at `.github/workflows/ci.yml` installs dependencies
and runs a compile check on the `app` package.

## Notes

- Redis connection is configured via `REDIS_HOST` and `REDIS_PORT`.
- Prometheus scrapes `/metrics` from the API container.
