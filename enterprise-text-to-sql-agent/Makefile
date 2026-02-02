.PHONY: venv install init-db show-schema ask smoke demo eval test lint docker-build docker-run docker-smoke

PY ?= python3
VENV ?= .venv
VPY := $(VENV)/bin/python
VPIP := $(VPY) -m pip

venv:
	$(PY) -m venv $(VENV)
	$(VPY) -m ensurepip --upgrade || true
	$(VPIP) install --upgrade pip setuptools wheel

install: venv
	$(VPIP) install -e .

init-db: install
	$(VPY) -m text2sql_agent.cli init-db

show-schema: install
	$(VPY) -m text2sql_agent.cli show-schema

ask: install
	$(VPY) -m text2sql_agent.cli ask "order fill rate last 30 days"

smoke: init-db show-schema ask

demo: install
	$(VPY) -m text2sql_agent.cli ask "order fill rate last 30 days"
	$(VPY) -m text2sql_agent.cli ask "order fill rate"

eval: install
	$(VPY) -m text2sql_agent.cli eval

test: install
	$(VPY) -m pytest

lint: install
	$(VPY) -m ruff check src tests eval

docker-build:
	docker build -t text2sql-agent .

docker-run:
	docker run --rm -p 8000:8000 text2sql-agent

docker-smoke:
	bash scripts/docker_smoke.sh
