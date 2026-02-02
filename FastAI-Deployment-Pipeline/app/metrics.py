from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

HIT_COUNTER = Counter("hit_requests_total", "Total number of POST /hit calls")
REDIS_COUNT = Gauge("redis_hit_count", "Current hit count stored in Redis")


def record_hit(current_count: int) -> None:
    HIT_COUNTER.inc()
    REDIS_COUNT.set(current_count)


def record_current_count(current_count: int) -> None:
    REDIS_COUNT.set(current_count)


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
