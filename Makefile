.PHONY: help install test test-all cov lint format check examples readme readme-check version bump-patch bump-minor bump-major clean build publish

PYTHON_VERSIONS := 3.10 3.11 3.12 3.13 3.14

help:
	@echo "make install       - install/sync dev dependencies"
	@echo "make test          - run tests on the project's Python"
	@echo "make test-all      - run tests against every supported Python ($(PYTHON_VERSIONS))"
	@echo "make cov           - run tests with coverage report"
	@echo "make lint          - run ruff lint"
	@echo "make format        - run ruff format (modifies files)"
	@echo "make check         - run lint + format check + readme-check"
	@echo "make examples      - regenerate SVG outputs from examples/*.py"
	@echo "make readme        - regenerate README.md from cog markers"
	@echo "make readme-check  - check README.md is up-to-date with cog (no changes)"
	@echo "make version       - show the current project version"
	@echo "make bump-patch    - bump patch version (0.4.1 -> 0.4.2)"
	@echo "make bump-minor    - bump minor version (0.4.1 -> 0.5.0)"
	@echo "make bump-major    - bump major version (0.4.1 -> 1.0.0)"
	@echo "make clean         - remove dist/"
	@echo "make build         - clean and build wheel + sdist"
	@echo "make publish       - test-all + readme-check + build, then publish to PyPI"

install:
	uv sync

test:
	uv run pytest

test-all:
	@for v in $(PYTHON_VERSIONS); do \
		echo "==> Python $$v"; \
		env -u VIRTUAL_ENV UV_PROJECT_ENVIRONMENT=.venvs/py$$v \
			uv run --python $$v pytest -q || exit 1; \
	done

cov:
	uv run pytest --cov=svg_helpers --cov-report=term-missing

lint:
	uv run ruff check svg_helpers/ tests/

format:
	uv run ruff format svg_helpers/ tests/ examples/

check:
	uv run ruff check svg_helpers/ tests/
	uv run ruff format --check svg_helpers/ tests/
	uv run cog --check README.md

examples:
	@cd examples && for f in *.py; do \
		echo "==> $$f"; \
		uv run python "$$f" || exit 1; \
	done

readme: examples
	uv run cog -r README.md

readme-check:
	uv run cog --check README.md

version:
	uv version

bump-patch:
	uv version --bump patch

bump-minor:
	uv version --bump minor

bump-major:
	uv version --bump major

clean:
	rm -rf dist/

build: clean
	uv build

publish: test-all readme-check build
	uv publish
