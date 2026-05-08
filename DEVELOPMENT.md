# Development

Notes for future me on the dev workflow. End-user documentation is in
[README.md](README.md).

The project intentionally stays small. Before adding a feature,
re-read the goals and anti-goals in the README — "comprehensive" is
an explicit anti-goal.

## Setup

```bash
uv sync
uv run pre-commit install   # one-time, enables the pre-commit hooks
```

Most operations have a `make` target. Run `make help` for the list.

## Development workflow

```bash
make test         # run the test suite (~40 tests, runs in <1s)
make cov          # tests with coverage report (should stay at 100% lines)
make lint         # ruff check
make format       # ruff format (modifies files in place)
make check        # lint + format-check + readme-check (the "is the codebase clean?" gate)
```

The pre-commit hooks run `ruff`, `ruff format`, and `cog --check` on
every commit. Anything that would block CI gets caught locally.

## Adding or modifying a runnable example

Each runnable example lives as a standalone script in `examples/` and
generates its own SVG output. The README's code blocks and image
references are generated from these scripts via [cog].

To add a new example:

1. Write `examples/my_example.py`. It should `svg.save(Path(__file__).parent / "my_example.svg")` at the end.
2. Add a section to `README.md` with a cog marker pair:
   ```markdown
   <!-- [[[cog example("my_example", "Alt text") ]]] -->
   <!-- [[[end]]] -->
   ```
3. Run `make readme`. This runs all example scripts (regenerating their SVGs) and runs cog (regenerating the code blocks and image references between every marker pair).
4. Commit the script, the SVG, and the updated README together.

To modify an existing example, edit the script and run `make readme`.
The pre-commit hook runs `cog --check`; if the README is out of sync
with any script, the commit fails with a clear message.

## Release flow

```bash
# 1. Develop on main (or a branch). If you touched any examples/*.py:
make readme        # regenerate SVGs and README

# 2. Sanity-check
make check         # lint + format-check + readme-check
make test

# 3. Commit and push (pre-commit fires; cog --check runs automatically)
git add ...
git commit -m "..."
git push           # required: the README's image links resolve to
                   # raw.githubusercontent.com URLs, so the SVGs must
                   # be on GitHub before the package is published

# 4. Bump the version (updates pyproject.toml and uv.lock together)
make bump-patch    # 0.4.1 -> 0.4.2
# or:
make bump-minor    # 0.4.1 -> 0.5.0
make bump-major    # 0.4.1 -> 1.0.0

# 5. Commit and push the bump
git add pyproject.toml uv.lock
git commit -m "v0.4.2"
git push

# 6. Publish (requires $UV_PUBLISH_TOKEN in the environment)
make publish
```

`make publish` runs `readme-check` before building. If the README is
stale, it fails before anything reaches PyPI.

`svg_helpers.__version__` is read from the installed package metadata
via `importlib.metadata`, so it stays in sync with `pyproject.toml`
automatically — no second place to update on release.

## Three layers of "the README is up to date"

1. **Pre-commit** — `cog --check` fires on every commit that touches `README.md` or any `examples/*.py` file.
2. **`make check`** — same check, runs as part of the manual gate.
3. **`make publish`** — runs the check immediately before building. Last line of defense.

If you forget `make readme` after editing a script, one of these
catches it before anything reaches PyPI.

## Three layers of "the example code actually works"

1. **`make readme`** runs each example script directly. A script that crashes never produces an SVG.
2. **The test suite** (`make test`) verifies the library code itself with 100% line coverage.
3. **The pre-commit hook** runs cog over the README. If a script imports something broken, cog's run will fail.

[cog]: https://github.com/nedbat/cog
