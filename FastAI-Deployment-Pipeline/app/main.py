import os

import redis
from fastapi import FastAPI, HTTPException, Response

from app.metrics import record_current_count, record_hit, render_metrics

REDIS_KEY = "hit_count"


def build_redis_client() -> redis.Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    return redis.Redis(host=host, port=port, decode_responses=True)


app = FastAPI(title="fastapi-deployment-pipeline")


@app.on_event("startup")
def startup() -> None:
    app.state.redis = build_redis_client()
    try:
        app.state.redis.ping()
    except redis.RedisError as exc:
        raise RuntimeError("Redis connection failed") from exc


@app.post("/hit")
def hit() -> dict:
    try:
        count = app.state.redis.incr(REDIS_KEY)
        record_hit(int(count))
        return {"count": int(count)}
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc


@app.get("/stats")
def stats() -> dict:
    try:
        value = app.state.redis.get(REDIS_KEY)
        count = int(value) if value is not None else 0
        record_current_count(count)
        return {"count": count}
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    data, content_type = render_metrics()
    return Response(content=data, media_type=content_type)
