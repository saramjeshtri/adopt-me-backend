install:
	uv venv && \
	. .venv/bin/activate && \
	uv sync

format:
	ruff format .

lint-check:
	ruff check

lint-fix:
	ruff check --fix

local:
	uv run main.py