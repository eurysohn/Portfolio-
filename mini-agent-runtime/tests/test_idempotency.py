import time

from runtime.idempotency import IdempotencyStore


def test_idempotency_store_ttl_expiry():
    store = IdempotencyStore(ttl_s=0.01)
    store.set("key-1", {"ok": True})
    assert store.get("key-1") == {"ok": True}
    time.sleep(0.02)
    assert store.get("key-1") is None
