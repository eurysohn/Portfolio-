from runtime.state import MemoryStore, SessionEntry


def test_memory_store_appends_and_trims():
    store = MemoryStore(max_entries=2)
    store.append(
        "session-1",
        SessionEntry(
            ticket="t1",
            route="runbook_lookup",
            confidence=0.9,
            tool_results=[],
            escalated=False,
            timestamp=1.0,
        ),
    )
    store.append(
        "session-1",
        SessionEntry(
            ticket="t2",
            route="data_query",
            confidence=0.7,
            tool_results=[],
            escalated=False,
            timestamp=2.0,
        ),
    )
    store.append(
        "session-1",
        SessionEntry(
            ticket="t3",
            route="escalate",
            confidence=0.2,
            tool_results=[],
            escalated=True,
            timestamp=3.0,
        ),
    )
    state = store.get_or_create("session-1")
    assert len(state.history) == 2
    assert state.history[0].ticket == "t2"
    assert state.history[1].ticket == "t3"
