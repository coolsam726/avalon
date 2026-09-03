.PHONY: help smoke regression test test-cov lint

PYTHON ?= .venv/bin/python
PYTEST ?= $(PYTHON) -m pytest

help:
	@echo "make smoke       - milestone smoke gate (no coverage)"
	@echo "make regression  - smoke + contract regression tests (no coverage)"
	@echo "make test        - full unit + smoke suite (no coverage)"
	@echo "make test-cov    - full suite with coverage fail-under 95%"
	@echo "make lint        - ruff check"

smoke:
	$(PYTEST) -q tests/smoke -m smoke

regression:
	$(PYTEST) -q -m regression

test:
	$(PYTEST) -q

test-cov:
	$(PYTEST) -q --cov=avalon --cov-report=term-missing --cov-report=xml

lint:
	$(PYTHON) -m ruff check src tests
