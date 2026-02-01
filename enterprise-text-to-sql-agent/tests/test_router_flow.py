import sqlite3

from text2sql_agent.agent import AgentConfig, Text2SQLAgent


def _init_db(tmp_path) -> str:
    db_path = tmp_path / "app.db"
    seed = "data/seed.sql"
    with sqlite3.connect(db_path) as conn:
        with open(seed, "r", encoding="utf-8") as handle:
            conn.executescript(handle.read())
    return str(db_path)


def test_agent_success_flow(tmp_path):
    db_path = _init_db(tmp_path)
    agent = Text2SQLAgent(AgentConfig(db_url=f"sqlite:///{db_path}"))
    response = agent.ask("order fill rate last 30 days")
    assert response["outcome_type"] == "SUCCESS"
    assert response["sql"] is not None
    assert response["result"]["summary"]["value"] is not None


def test_agent_safe_error_on_unsafe_keyword(tmp_path):
    db_path = _init_db(tmp_path)
    agent = Text2SQLAgent(AgentConfig(db_url=f"sqlite:///{db_path}"))
    response = agent.ask("drop table orders")
    assert response["outcome_type"] == "SAFE_ERROR"
