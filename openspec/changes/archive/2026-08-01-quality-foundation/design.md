## Context

The project is a new Python application targeting Linux/Wayland. No quality tools are currently configured. The goal is to establish a complete quality foundation before application development begins in subsequent sprints.

Constraints:
- Python 3.13+
- uv as package manager
- Minimal dependencies
- Fast execution
- Linux-focused development

## Goals / Non-Goals

**Goals:**
- Provide automatic code formatting
- Validate code quality through linting
- Verify type annotations
- Execute unit tests
- Run quality checks before commits
- Execute all checks in CI on pull requests
- Provide a single command to run all checks locally

**Non-Goals:**
- Application functionality (device detection, event handling, etc.)
- Code coverage enforcement (future consideration)
- Performance optimization of quality tools
- Integration with external quality services

## Decisions

### Decision 1: Use ruff for formatting and linting

**Choice:** ruff

**Rationale:** ruff is a modern Python tool that combines formatting and linting in a single, extremely fast tool written in Rust. It replaces multiple tools (black, isort, flake8, etc.) with one unified solution, reducing configuration complexity and execution time.

**Alternatives considered:**
- black + flake8 + isort: Multiple tools with overlapping responsibilities, slower execution
- autopep8 + pylint: Older tools, less comprehensive, slower

### Decision 2: Use mypy for type checking

**Choice:** mypy

**Rationale:** mypy is the most widely adopted static type checker for Python with excellent IDE integration and comprehensive type inference. It's the reference implementation for PEP 484 and has strong community support.

**Alternatives considered:**
- pyright: Faster but less mature, smaller ecosystem
- pytype: Google-maintained, less community adoption

### Decision 3: Use pytest for testing

**Choice:** pytest

**Rationale:** pytest is the de facto standard for Python testing with a simple syntax, powerful fixtures, and extensive plugin ecosystem. It requires minimal configuration and integrates well with modern Python practices.

**Alternatives considered:**
- unittest: Built-in but more verbose, less flexible
- nose2: Less actively maintained

### Decision 4: Use pre-commit for hooks

**Choice:** pre-commit

**Rationale:** pre-commit is the standard tool for managing git hooks in Python projects. It provides a unified configuration format, automatic updates, and supports hooks from multiple ecosystems. It's widely adopted and well-documented.

**Alternatives considered:**
- Custom git hooks: Manual maintenance, no update mechanism
- lefthook: Less Python-focused, smaller community

### Decision 5: Use GitHub Actions for CI

**Choice:** GitHub Actions

**Rationale:** The project is hosted on GitHub, making GitHub Actions the natural choice for CI. It's tightly integrated with pull requests, requires no external service setup, and has a large marketplace of pre-built actions.

**Alternatives considered:**
- CircleCI: External service, additional configuration
- Travis CI: Less integrated with GitHub, slower adoption

### Decision 6: Provide a single validation command via uv

**Choice:** Use uv scripts or a Makefile

**Rationale:** Since the project uses uv, we can leverage uv's script execution or provide a simple Makefile to run all quality checks in sequence. This provides a consistent interface for developers.

**Alternatives considered:**
- Shell script: Less portable, requires manual execution
- tox: Additional dependency, more complex configuration

## Risks / Trade-offs

**Risk:** Tool configuration conflicts
→ **Mitigation:** Use ruff's unified configuration to minimize conflicts between formatting and linting rules

**Risk:** Slow CI execution
→ **Mitigation:** ruff is extremely fast; use pytest-xdist for parallel test execution if needed

**Risk:** Pre-commit hook failures frustrate developers
→ **Mitigation:** Provide clear error messages and documentation; hooks run quickly with ruff

**Risk:** Type checking reveals many issues in existing code
→ **Mitigation:** Sprint 0.5 has no application code yet; start with strict mode from the beginning

**Trade-off:** ruff is newer than black/flake8
→ **Acceptance:** ruff's speed and unified approach outweigh the risk; it's rapidly becoming the standard

**Trade-off:** mypy is slower than pyright
→ **Acceptance:** mypy's maturity and ecosystem support justify the slight performance cost
