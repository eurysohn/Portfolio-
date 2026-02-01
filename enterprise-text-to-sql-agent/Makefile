.PHONY: setup init-db demo eval test lint

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install -e ".[dev]"

init-db:
	python -m text2sql_agent.cli init-db

demo:
	python -m text2sql_agent.cli ask "order fill rate last 30 days"
	python -m text2sql_agent.cli ask "order fill rate"

eval:
	python -m text2sql_agent.cli eval

test:
	pytest

lint:
	ruff check src tests eval
