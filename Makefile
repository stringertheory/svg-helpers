.PHONY: help install test cov lint format check clean build publish

help:
	@echo "make install  - install/sync dev dependencies"
	@echo "make test     - run tests"
	@echo "make cov      - run tests with coverage report"
	@echo "make lint     - run ruff lint"
	@echo "make format   - run ruff format (modifies files)"
	@echo "make check    - run lint + format check (no modifications)"
	@echo "make clean    - remove dist/"
	@echo "make build    - clean and build wheel + sdist"
	@echo "make publish  - build and publish to PyPI"

install:
	uv sync

test:
	uv run pytest

cov:
	uv run pytest --cov=svg_helpers --cov-report=term-missing

lint:
	uv run ruff check svg_helpers/ tests/

format:
	uv run ruff format svg_helpers/ tests/

check:
	uv run ruff check svg_helpers/ tests/
	uv run ruff format --check svg_helpers/ tests/

clean:
	rm -rf dist/

build: clean
	uv build

publish: build
	UV_PUBLISH_TOKEN="$$POETRY_PYPI_TOKEN_PYPI" uv publish
