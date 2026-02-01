PYTHON ?= python3.11

.PHONY: setup run demo test lint format

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) -m runtime.cli run

demo:
	$(PYTHON) -m runtime.cli demo

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format:
	$(PYTHON) -m ruff format .
