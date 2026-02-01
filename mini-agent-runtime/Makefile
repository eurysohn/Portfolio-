PYTHON ?= python3

.PHONY: setup run demo test lint format ui

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) -m runtime.cli run

demo:
	$(PYTHON) -m runtime.cli demo

ui:
	$(PYTHON) -m runtime.api

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format:
	$(PYTHON) -m ruff format .
