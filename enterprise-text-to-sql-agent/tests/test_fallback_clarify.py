import sqlite3

from text2sql_agent.agent import AgentConfig, Text2SQLAgent


def test_clarify_when_missing_time_window(tmp_path):
    db_path = tmp_path / "app.db"
    with sqlite3.connect(db_path) as conn:
        with open("data/seed.sql", "r", encoding="utf-8") as handle:
            conn.executescript(handle.read())
    agent = Text2SQLAgent(AgentConfig(db_url=f"sqlite:///{db_path}"))
    response = agent.ask("order fill rate")
    assert response["outcome_type"] == "CLARIFY"
    assert response["clarification"] is not None
