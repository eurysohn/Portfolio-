import sqlite3

from eval.run_eval import run_eval


def test_eval_runner_outputs_metrics(tmp_path):
    db_path = "data/app.db"
    with sqlite3.connect(db_path) as conn:
        with open("data/seed.sql", "r", encoding="utf-8") as handle:
            conn.executescript(handle.read())
    metrics = run_eval()
    assert metrics["total_cases"] >= 50
    assert "sql_match_rate" in metrics
