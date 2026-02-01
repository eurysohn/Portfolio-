import sqlite3

from text2sql_agent.executor import SQLExecutor


def test_executor_returns_rows(tmp_path):
    db_path = tmp_path / "app.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE demo (value INTEGER)")
        conn.executemany("INSERT INTO demo VALUES (?)", [(1,), (2,), (3,)])
    executor = SQLExecutor(f"sqlite:///{db_path}")
    result = executor.run("SELECT SUM(value) AS value FROM demo", {})
    assert result.row_count == 1
    assert result.rows[0]["value"] == 6
