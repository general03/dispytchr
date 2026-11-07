APP := src/dispytchr/asgi.py
HOST ?= 127.0.0.1
PORT ?= 8000

.DEFAULT_GOAL := help
.PHONY: help install lock dev run test lint format typecheck check clean

help:
	@grep -E '^[a-z-]+:' $(MAKEFILE_LIST) | cut -d: -f1 | sort

install:
	uv sync
	uv run pre-commit install

lock:
	uv lock

dev:
	uv run fastapi dev $(APP) --host $(HOST) --port $(PORT)

run:
	uv run fastapi run $(APP) --host $(HOST) --port $(PORT)

test:
	uv run pytest --cov

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy

check: lint typecheck test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov coverage.xml dist build
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
