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
- MouseFlow is intended to be small — every dependency, abstraction, and feature should justify its existence.
- Prefer the standard library unless there is a compelling reason not to.

---

# Domain Modeling

MouseFlow has its own domain. Core concepts must be represented by domain objects, not primitive values, when doing so adds clarity or type safety.

The domain model is the public API of the project. Components communicate by exchanging domain objects, not loose data structures.

## Principles

- Infrastructure converts external data into domain objects as early as possible.
- The domain never knows about infrastructure details (evdev, i3ipc, file formats, etc.).
- Domain objects are immutable by default.
- Prefer explicit modeling over clever abstractions.

See `docs/architecture.md` for the complete list of domain objects and their relationships.

---

# Architectural Boundaries

Each component has clear responsibilities. Mixing concerns is not allowed.

See `docs/architecture.md` for detailed component descriptions, data flow, and dependency graph.

---

# Decision Making

When multiple valid implementations exist, prioritize in this order:

1. **Simplicity** — Choose the simplest solution that works.
2. **Clean domain** — Prefer solutions that keep the domain model clear and expressive.
3. **Low coupling** — Minimize dependencies between components.
4. **Fewer dependencies** — Prefer standard library over external packages.
5. **Readability** — Code is read more than written.
6. **Testability** — Every feature must be testable in isolation.
7. **Long-term maintainability** — Avoid cleverness; optimize for future developers.

When in doubt, choose the option that leaves the codebase easier to understand.

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