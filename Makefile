.PHONY: help install test cov lint format check examples readme readme-check version bump-patch bump-minor bump-major clean build publish

help:
	@echo "make install       - install/sync dev dependencies"
	@echo "make test          - run tests"
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
	@echo "make publish       - build and publish to PyPI"

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
	uv run cog --check README.md

examples:
	cd examples && uv run python japan.py
	cd examples && uv run python banana.py
	cd examples && uv run python circle.py
	cd examples && uv run python text.py

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

publish: readme-check build
	uv publish
