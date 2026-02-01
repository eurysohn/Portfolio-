import argparse
import json
import os
import sqlite3
from typing import Any

from .agent import AgentConfig, Text2SQLAgent
from .schema import SchemaCache, introspect_schema, schema_as_dict


def _init_db(db_path: str, seed_path: str) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        with open(seed_path, "r", encoding="utf-8") as handle:
            conn.executescript(handle.read())


def _ask(question: str, scope: str) -> dict[str, Any]:
    agent = Text2SQLAgent(AgentConfig(db_url=f"sqlite:///{_db_path()}"))
    return agent.ask(question, scope=scope)


def _show_schema() -> dict[str, Any]:
    snapshot = introspect_schema(f"sqlite:///{_db_path()}", SchemaCache())
    return schema_as_dict(snapshot)


def _db_path() -> str:
    return "data/app.db"


def main() -> None:
    parser = argparse.ArgumentParser(description="Enterprise Text-to-SQL agent")
    sub = parser.add_subparsers(dest="command", required=True)

    init_db = sub.add_parser("init-db", help="Initialize SQLite database")
    init_db.add_argument("--db", default=_db_path())
    init_db.add_argument("--seed", default="data/seed.sql")

    ask = sub.add_parser("ask", help="Ask a KPI question")
    ask.add_argument("question")
    ask.add_argument("--scope", default="default")

    sub.add_parser("show-schema", help="Show cached schema")
    sub.add_parser("eval", help="Run evaluation harness")

    args = parser.parse_args()

    if args.command == "init-db":
        _init_db(args.db, args.seed)
        print(f"Initialized database at {args.db}")
    elif args.command == "ask":
        result = _ask(args.question, args.scope)
        print(json.dumps(result, indent=2))
    elif args.command == "show-schema":
        schema = _show_schema()
        print(json.dumps(schema, indent=2))
    elif args.command == "eval":
        from eval.run_eval import run_eval

        metrics = run_eval()
        print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
