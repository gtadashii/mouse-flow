# Mouse Flow

Per-application mouse actions for Wayland compositors.

## Development

### Setup

```bash
uv sync --extra dev
pre-commit install
```

### Quality Checks

Run all quality checks:

```bash
make check
```

Or run individually:

```bash
make format    # Check formatting
make lint      # Run linter
make typecheck # Type checking
make test      # Run tests
```

**Note:** The Makefile uses `.venv/bin/` directly, so you don't need `uv` in your PATH after initial setup.

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit. They check:
- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Tests (pytest)

To run manually:

```bash
pre-commit run --all-files
```
