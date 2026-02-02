# Contributing

## Development Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up pre-commit or run quality checks manually.

## Quality Standards
Before submitting a PR, ensure:
- **Linting**: No `ruff` errors.
- **Typing**: `mypy .` passes.
- **Tests**: `pytest` passes with 100% coverage on core logic.

## Branching & Commits
- Use **Conventional Commits** (e.g., `feat:`, `fix:`, `docs:`, `chore:`).
- Branch names: `feature/description` or `fix/description`.
