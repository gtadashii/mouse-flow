## 1. Dependencies Setup

- [x] 1.1 Add development dependencies to pyproject.toml (ruff, mypy, pytest, pre-commit)
- [x] 1.2 Install dependencies with uv

## 2. Code Formatting Configuration

- [x] 2.1 Configure ruff formatter in pyproject.toml (line length, target Python version)
- [x] 2.2 Format existing code with ruff format
- [x] 2.3 Verify formatting works correctly

## 3. Code Linting Configuration

- [x] 3.1 Configure ruff linter in pyproject.toml (select rules, ignore rules)
- [x] 3.2 Run ruff check on existing code
- [x] 3.3 Fix any linting violations or adjust configuration

## 4. Type Checking Configuration

- [x] 4.1 Configure mypy in pyproject.toml or mypy.ini (strict mode, Python version)
- [x] 4.2 Run mypy on existing code
- [x] 4.3 Fix any type errors or adjust configuration

## 5. Testing Configuration

- [x] 5.1 Configure pytest in pyproject.toml (test paths, options)
- [x] 5.2 Create tests directory structure
- [x] 5.3 Add a sample test to verify pytest works
- [x] 5.4 Run pytest to verify configuration

## 6. Pre-commit Hooks

- [x] 6.1 Create .pre-commit-config.yaml with ruff, mypy, and pytest hooks
- [x] 6.2 Install pre-commit hooks with `pre-commit install`
- [x] 6.3 Test pre-commit hooks on a sample commit
- [x] 6.4 Verify hooks block invalid commits

## 7. GitHub Actions CI

- [x] 7.1 Create .github/workflows/ci.yml workflow file
- [x] 7.2 Configure workflow to run on pull requests
- [x] 7.3 Add steps for ruff format check, ruff check, mypy, and pytest
- [x] 7.4 Test workflow by creating a draft pull request

## 8. Single Command Validation

- [x] 8.1 Create Makefile with `check` target that runs all quality checks
- [x] 8.2 Verify `make check` runs formatting, linting, type checking, and tests
- [x] 8.3 Document the validation command in README or AGENTS.md

## 9. Final Verification

- [x] 9.1 Run all quality checks locally and verify they pass
- [x] 9.2 Create a test pull request to verify CI pipeline
- [x] 9.3 Verify pre-commit hooks work on a real commit
- [x] 9.4 Update documentation with quality standards
