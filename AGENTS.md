# MouseFlow

## Project Overview

MouseFlow is an open-source Linux application that enables per-application mouse actions, inspired by Logitech Options+, but designed specifically for Wayland compositors.

The project focuses on simplicity, clean architecture, and long-term maintainability.

Primary development target:

- Linux
- Wayland
- Sway

Future compositor support should be possible without major architectural changes.

---

# Vision

MouseFlow should become the simplest and most extensible mouse automation tool for Wayland.

Examples:

- Browser back/forward
- Workspace switching
- Tab navigation
- Mouse gestures
- Thumb wheel actions
- Application-specific shortcuts

---

# Project Goals

The project has two equally important goals.

## 1. Build a production-quality application

The codebase should be suitable for long-term maintenance and open-source collaboration.

## 2. Learn modern Python

The project intentionally explores modern Python features and best practices, including:

- typing
- dataclasses
- protocols
- pathlib
- context managers
- generators
- async (only if necessary)
- packaging
- testing

Learning is part of the project.

---

# Engineering Principles

- Keep the architecture simple.
- Prefer composition over inheritance.
- Avoid unnecessary dependencies.
- Every module should have a single responsibility.
- Every feature should be testable.
- Small pull requests are preferred.
- Optimize for readability over cleverness.

---

# Development Process

Development follows Specification Driven Development (SDD) combined with Test-Driven Development (TDD).

Every feature follows this workflow:

1. Product Requirement Document (PRD)
2. Specification
3. TDD cycle (Red → Green → Refactor):
   - **Red**: Write failing tests that define the expected behavior
   - **Green**: Write the minimum implementation to make tests pass
   - **Refactor**: Improve code quality while keeping tests green
4. Review

Implementation should never start before the specification is approved.
Tests must always be written before the implementation they validate.

---

# Code Style

Prefer:

- explicit code
- pure functions where possible
- immutable data
- descriptive names
- complete type annotations

Avoid:

- global state
- hidden side effects
- premature optimization
- unnecessary abstractions

---

# Technologies

Current stack:

- Python
- uv
- evdev
- Wayland
- Sway
- YAML
- systemd
- GitHub Actions

---

# Project Philosophy

MouseFlow is intended to be small.

Every dependency, abstraction, and feature should justify its existence.

If something can be implemented with the Python standard library, prefer it unless there is a compelling reason not to.