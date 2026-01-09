# Repository Guidelines

## Project Structure & Module Organization
- `main.py` / `kaja/__main__.py`: PySide6 entry point that prepares fonts and launches the UI (`kaja/ui`).
- `kaja/core`: pipeline, pricing, diagnostics, and settings logic; primary place for feature work.
- `kaja/ui` and `kaja/components`: Qt windows/dialogs and shared UI pieces.
- `doc/`: product briefs and request templates; align changes with these contracts.
- `resources/`: bundled fonts and other UI assets; keep in sync with `_register_fonts`.
- Runtime dirs: `IN/` inputs, `OUT/` generated output, `LOG/` diagnostics; avoid committing artifacts.
- Support files: `requirements.txt`, `settings.json`, `pricing_cache.json`, `kaja.db` (local state).

## Build, Test, and Development Commands
- Create env and install deps: `python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt`.
- Run the app: `python main.py` (or `python -m kaja`).
- Quick OpenAI connectivity check: `python test_openai.py` (requires `OPENAI_API_KEY`).
- Full test suite: `python -m pytest`. Export `OPENAI_API_KEY` before running to satisfy `test_openai.py`.

## Coding Style & Naming Conventions
- Python 3 with type hints throughout core modules; follow PEP 8 (4-space indents, snake_case for functions/vars, PascalCase for classes).
- Prefer f-strings, early returns, and small pure helpers in `kaja/core`.
- Keep UI code declarative and signal-driven; avoid long slot methods—factor into helpers in `kaja/components`.
- Localized strings/logs already include Czech text; preserve existing phrasing and encoding.

## Testing Guidelines
- Place tests as `test_*.py` near the code or under a dedicated tests folder; mirror module names.
- Always run `python -m pytest` before pushing; add regression tests for pipeline and UI logic where feasible.
- For network-bound tests, guard with environment checks and provide deterministic fixtures/mocks when possible.
- Record the commands and outcomes when adding or modifying tests.

## Commit & Pull Request Guidelines
- Current history uses milestone-style commits/tags (`milestone-YYYYMMDDHHMM`). Keep milestones for checkpoints; use clear, descriptive messages for functional changes.
- Reference related tasks/issues in the body; list user-visible changes and risks.
- For UI changes, include before/after screenshots (e.g., from `OUT/`).
- Note test commands run (e.g., `python -m pytest`) and any env vars required (`OPENAI_API_KEY`).

## Security & Configuration
- Never commit secrets; set `OPENAI_API_KEY` in your environment for API and test calls.
- `settings.json` is auto-generated on first run; review paths before committing changes.
- Treat `kaja.db`, `LOG/`, and `OUT/` as local artifacts unless explicitly needed for debugging.
