import sqlite3

from text2sql_agent.agent import AgentConfig, Text2SQLAgent
from text2sql_agent.cache import FileCache


def test_cache_hit_on_repeat_question(tmp_path):
    db_path = tmp_path / "app.db"
    cache_path = tmp_path / "cache.json"
    with sqlite3.connect(db_path) as conn:
        with open("data/seed.sql", "r", encoding="utf-8") as handle:
            conn.executescript(handle.read())
    cache = FileCache(str(cache_path))
    agent = Text2SQLAgent(AgentConfig(db_url=f"sqlite:///{db_path}"), cache=cache)
    first = agent.ask("total revenue last 30 days")
    second = agent.ask("total revenue last 30 days")
    assert first.get("cache_hit") is False
    assert second.get("cache_hit") is True
