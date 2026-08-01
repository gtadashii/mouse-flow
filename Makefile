.PHONY: check format lint typecheck test

VENV := .venv/bin

check: format lint typecheck test

format:
	$(VENV)/ruff format --check src/ tests/

lint:
	$(VENV)/ruff check src/ tests/

typecheck:
	$(VENV)/mypy src/

test:
	$(VENV)/pytest
