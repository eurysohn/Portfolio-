import json
from pathlib import Path

from observability.tracing import TraceEvent, TraceStore, now_ts


def test_trace_store_persist_and_load(tmp_path: Path):
    jsonl_path = tmp_path / "traces.jsonl"
    store = TraceStore(jsonl_path=str(jsonl_path))
    event = TraceEvent(
        run_id="run-1",
        trace_id="trace-1",
        correlation_id="corr-1",
        event_type="test",
        message="hello",
        data={"key": "value"},
        timestamp=now_ts(),
    )
    store.record(event)
    assert json.loads(jsonl_path.read_text(encoding="utf-8").strip())["run_id"] == "run-1"
    loaded = store.load_from_jsonl("run-1")
    assert len(loaded) == 1
