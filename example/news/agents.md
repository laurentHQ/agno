# Finance News AgentOS Guidelines

## Layout & Ownership
All Python sources live under `src/` (`agents/`, `api/`, `core/`, `utils/`) with shared helpers exposed through package `src`. Configuration stays in `config/` (copy `.env.example` before running); generated artifacts belong in `data/` (`data/reports/`, `data/databases/`). Frontend assets sit in `web/`, Docker assets in `docker/`, and runnable docs live in `docs/`. Keep notebooks, local notes, or large exports outside the repo or stash them under `reports/` if they document runs.

## Environment & Dependencies
Target Python 3.11+. Create a virtualenv at the project root and install dependencies with `pip install -r requirements/requirements-news.txt`; add `requirements-agentos.txt` for serving AgentOS and `requirements-github.txt` when working on GitHub scraping. Node 18+ is required for the web UI (`npm install` inside `web/`). Always bootstrap secrets with `cp config/.env.example .env` and keep API keys out of version control.

## Core Commands
Use `python -m src.api.finance_agentos_lite` for fast local loops, or `./scripts/start_agentos.sh [lite|dev|docker]` to match deployment modes. Fire up the web dashboard via `./scripts/start_webui.sh`. Configuration walkthroughs are automated by `./scripts/configure.sh`, which wires model credentials. Run the multi-check harness `./scripts/test_compilation.sh` before publishing; it compiles modules, lints with Ruff, and runs type checks when available.

## Coding Standards
Ruff enforces a 100-character limit, four-space indentation, double-quoted strings, and Bandit/Pylint extensions—run `./scripts/ruff_check.sh --fix` to stay aligned. Prefer explicit relative imports from `src.*` modules and keep long-running jobs behind scheduler abstractions in `src/core/`. Commit utility scripts under `scripts/` and ensure CLI entry points use `if __name__ == "__main__":`.

## Testing Expectations
Add or update tests in `tests/` using pytest discovery (`pytest tests/`); CLI-style scripts in that folder print diagnostics but still need assertions when you touch logic. When adding new agents or tools, provide smoke coverage mirroring `tests/test_finance_agent.py` and seed fixtures with `.env` guards so suites degrade gracefully without premium keys. Validate typings for critical modules with `./scripts/mypy_check.sh`.

## PR Checklist
Present scenarios in commit messages (`feat: add reddit trend agent` style) and gate every PR with lint, type check, and relevant pytest runs. Include a summary of manual verification (for example, `./scripts/start_agentos.sh lite`, `npm start`) and capture screenshots whenever the web UI or generated reports change. Document new environment flags in `config/.env.example` and note any schema migrations in `docs/`.
