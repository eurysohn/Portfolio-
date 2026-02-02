# Contributing

## Development Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`.
3. Create env file: `cp .env.example .env`.
4. Run locally: `python -m uvicorn api.main:app --port 8080 --reload`.

## Quality Standards
Before submitting a PR, ensure:
- **Linting**: `python -m ruff check .` passes.
- **Typing**: `python -m mypy .` passes.
- **Tests**: `python -m pytest` passes.

## Branching & Commits
- Use **Conventional Commits** (e.g., `feat:`, `fix:`, `docs:`, `chore:`).
- Branch names: `feature/description` or `fix/description`.

## PR Checklist
- Link the issue or TODO item you addressed.
- Add or update tests for logic changes.
- Update docs if you change public behavior or env vars.
