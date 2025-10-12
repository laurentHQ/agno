# Repository Guidelines

## Project Structure & Module Organization
The repo hosts two primary libraries under `libs/`: `libs/agno` contains the core agent framework (modules such as `agent/`, `models/`, `tools/`, `os/`, `workflow/`), while `libs/agno_infra` covers deployment helpers. Recipes and runnable demos live in `cookbook/`, and `example/` holds end-to-end sample apps. Tests are colocated in `libs/agno/tests` with `unit/` and `integration/` suites. Tooling scripts sit in `scripts/`, and generated reports (benchmarks, coverage) land in `reports/` and `coverage_report/`.

## Build, Test, and Development Commands
Install dependencies with `./scripts/dev_setup.sh`; it creates `.venv/` and installs packages via `uv pip`. Activate the environment (`source .venv/bin/activate`) before running commands. Format and sort imports with `./scripts/format.sh`, and run linters/type checks with `./scripts/validate.sh`, which invoke `ruff` and `mypy`. Execute the full test matrix across libraries through `./scripts/test.sh`; use `./libs/agno/scripts/test.sh` for library-only coverage, or call `pytest libs/agno/tests/unit/utils/test_string.py` for targeted debugging.

## Coding Style & Naming Conventions
Python code targets 3.9+ semantics with `ruff` enforcing a 120-character line length. Prefer four-space indentation, descriptive module names (e.g. `knowledge/reader`), and snake_case for functions and module constants. Public classes use PascalCase and should expose typed constructors. Run `ruff format` for whitespace and `ruff check --select I --fix` for import ordering; avoid manual formatting drift.

## Testing Guidelines
Follow the existing `test_*.py` naming and group scenarios under the parallel unit/integration directories. Unit tests should isolate single behaviors with fixtures from `libs/agno/tests/conftest.py`; integration tests can spin up AgentOS flows or database backends. All CI runs use coverage via `--cov=libs/agno/agno`. When adding a new provider or datastore, mirror the relevant cookbook recipe and add at least one regression test before invoking `./scripts/test.sh`.

## Commit & Pull Request Guidelines
Commits should remain small, imperative, and scoped (the current history favors one-line summaries such as `Update README`). For pull requests, use the required `[type] Subject` title tags (`[feat]`, `[fix]`, `[docs]`, etc.) and reference issues (`fixes #123`). Include a short summary of the change, validation steps, and screenshots or logs when altering AgentOS surfaces or tooling output. Ensure coverage/format scripts have run and link any cookbook additions directly so reviewers can exercise them quickly.

## Configuration Tips
Most features respect environment variables—set `AGNO_TELEMETRY=false` to disable telemetry when running local agents. Place secrets in `.env` files, load them with `pydantic-settings`, and avoid committing credentialed config.

## Subproject Guides
For the Finance News AgentOS example, follow the dedicated playbook in `example/news/agents.md`; create similar scoped guides alongside other complex examples.
