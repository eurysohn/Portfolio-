import logging
import os
import time
import uuid
from threading import Lock
from typing import Dict, Optional, Tuple

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.engine import run_agent
from config import settings

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
logging.basicConfig(level=settings.LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("scm_agent_api")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
    api_key: Optional[str] = None

METRICS_LOCK = Lock()
REQUEST_COUNTS: Dict[Tuple[str, str, int], int] = {}
REQUEST_LATENCY_SUM: Dict[Tuple[str, str], float] = {}
REQUEST_LATENCY_COUNT: Dict[Tuple[str, str], int] = {}
START_TIME = time.time()

def _record_metrics(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    with METRICS_LOCK:
        key = (method, path, status_code)
        REQUEST_COUNTS[key] = REQUEST_COUNTS.get(key, 0) + 1
        latency_key = (method, path)
        REQUEST_LATENCY_SUM[latency_key] = REQUEST_LATENCY_SUM.get(latency_key, 0.0) + duration_seconds
        REQUEST_LATENCY_COUNT[latency_key] = REQUEST_LATENCY_COUNT.get(latency_key, 0) + 1

def _render_metrics() -> str:
    # Minimal Prometheus-compatible text format without extra dependencies.
    lines = [
        "# HELP scm_api_uptime_seconds Seconds since process start.",
        "# TYPE scm_api_uptime_seconds gauge",
        f"scm_api_uptime_seconds {time.time() - START_TIME:.0f}",
        "# HELP scm_api_requests_total Total HTTP requests.",
        "# TYPE scm_api_requests_total counter",
    ]
    with METRICS_LOCK:
        for (method, path, status), count in sorted(REQUEST_COUNTS.items()):
            safe_path = path.replace('"', "")
            lines.append(
                f'scm_api_requests_total{{method="{method}",path="{safe_path}",status="{status}"}} {count}'
            )
        lines.append("# HELP scm_api_request_duration_seconds Average request duration.")
        lines.append("# TYPE scm_api_request_duration_seconds gauge")
        for (method, path), total in sorted(REQUEST_LATENCY_SUM.items()):
            count = REQUEST_LATENCY_COUNT.get((method, path), 1)
            safe_path = path.replace('"', "")
            lines.append(
                f'scm_api_request_duration_seconds{{method="{method}",path="{safe_path}"}} {total / count:.6f}'
            )
    return "\n".join(lines) + "\n"

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    response.headers["X-Correlation-ID"] = correlation_id
    _record_metrics(request.method, request.url.path, response.status_code, process_time)
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f correlation_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        process_time * 1000,
        correlation_id,
    )
    return response

# Serve static files from the "dist" directory
# This directory will be created by the frontend build process
dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend-ts", "dist")

@app.get("/")
async def serve_index():
    index_file = os.path.join(dist_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend build not found. Run 'npm run build' in frontend-ts directory."}

if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="static")

@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.ENV,
        "git_sha": settings.GIT_SHA,
    }

@app.get("/health")
async def health_check_alias():
    # Alias to prevent frontend health probes from 404-ing.
    return await health_check()

@app.post("/query")
async def query_agent(payload: QueryRequest, request: Request):
    if settings.REQUIRE_API_KEY and not payload.api_key:
        raise HTTPException(status_code=401, detail="OPENAI_API_KEY is required.")
    logger.info(
        "agent_query query_len=%s top_k=%s correlation_id=%s",
        len(payload.query),
        payload.top_k,
        request.state.correlation_id,
    )
    result = run_agent(payload.query, top_k=payload.top_k, api_key=payload.api_key)
    return result

@app.post("/api/query")
async def query_agent_alias(payload: QueryRequest, request: Request):
    # Alias for frontend builds that call /api/query without proxy.
    return await query_agent(payload, request)

@app.get("/api/healthz")
async def healthz_alias():
    return await health_check()

@app.get("/api/health")
async def health_alias():
    return await health_check()

@app.get("/metrics")
async def metrics():
    # TODO: Switch to prometheus_client for richer metrics once approved.
    return Response(content=_render_metrics(), media_type="text/plain; version=0.0.4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
