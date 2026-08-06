# MouseFlow Roadmap

## Vision

MouseFlow is an open-source Linux application that enables per-application mouse actions on Wayland compositors.

The project is intentionally developed in small, incremental iterations. Each sprint delivers a working piece of software while introducing new concepts of modern Python and clean architecture.

The roadmap represents the expected evolution of the project but may change as new learnings emerge.

---

# Roadmap

## Phase 0 — Bootstrap

### Goal

Create a modern Python project that can be executed locally.

### Deliverable

```bash
uv run mouseflow
```

Output:

```text
MouseFlow started.
```

---

## Phase 0.5 — Quality Foundation

### Goal

Establish the engineering standards for the project.

### Deliverables

- formatter
- linter
- type checking
- unit testing
- pre-commit hooks
- GitHub Actions

---

## Phase 1 — Device Discovery

### Goal

Automatically locate the supported mouse device.

### Deliverable

```text
Found device:

Logitech MX Master 3S
```

---

## Phase 2 — Input Engine

### Goal

Receive raw mouse events continuously.

### Deliverable

```text
BTN_SIDE

BTN_EXTRA

REL_HWHEEL
```

---

## Phase 3 — Window Resolver

### Goal

Identify the currently focused application.

### Deliverable

```text
Application

Firefox

Title

ChatGPT
```

---

## Phase 4 — Domain Model

### Goal

Define the core domain objects used throughout the application.

Examples:

- MouseEvent
- Application
- Action
- Gesture
- Profile

---

## Phase 5 — Event Dispatcher

### Goal

Associate input events with the active application.

### Deliverable

```text
Firefox

BTN_SIDE

↓

No action found.
```

---

## Phase 6 — Configuration Loader

### Goal

Load user-defined mappings from configuration files.

### Deliverable

```yaml
firefox:

  BTN_SIDE:

    keyboard: alt+left
```

---

## Phase 7 — Action Runner

### Goal

Execute configured actions.

Examples:

- keyboard shortcuts
- shell commands
- applications

---

## Phase 8 — Per-Application Profiles ✓ COMPLETE

### Goal

Allow different mappings depending on the focused application.

### Deliverable

Example:

Firefox

BTN_SIDE

↓

Alt+Left

VS Code

BTN_SIDE

↓

Ctrl+-

### Implementation

- ProfileResolver component with deterministic precedence
- Global profile fallback support
- YAML configuration with `global:` key
- Profile selection reporting

---

## Phase 9 — Mouse Gestures

### Goal

Recognize gesture movements while holding a mouse button.

### Features

- Direction-based gestures (up, down, left, right)
- Diagonal gestures (up-left, up-right, down-left, down-right)
- Gesture recognition while holding mouse buttons
- Configurable gesture actions per application

### Examples

- Swipe left → Workspace previous
- Swipe right → Workspace next
- Swipe up → Window maximize
- Swipe down → Window minimize
- Circular gesture → Custom shortcut

### Technical Considerations

- Gesture recognition engine as new pipeline stage
- Gesture domain objects (Gesture, GestureDirection)
- Integration with existing profile system
- Configurable gesture sensitivity

---

## Phase 10 — Thumb Wheel ✓ COMPLETE

### Goal

Support continuous horizontal wheel actions.

### Examples

- Browser tabs
- VS Code tabs
- Timeline navigation

### Implementation

- Dedicated InputIdentifier enum values (THUMB_WHEEL_LEFT, THUMB_WHEEL_RIGHT)
- REL_HWHEEL event mapping in Input Engine
- Pipeline integration without component modifications
- YAML configuration support for thumb wheel mappings

---

## Phase 11 — Daemon Mode ✓ COMPLETE

### Goal

Run MouseFlow as a background service.

### Implementation

- Dedicated `daemon.py` component for lifecycle management
- Logging infrastructure (stdlib `logging` module)
- Signal handling (SIGTERM, SIGINT) for graceful shutdown
- systemd user service integration (`packaging/mouseflow.service`)
- Entry point refactored to delegate to Daemon

Example:

```bash
systemctl --user enable mouseflow
```

---

## Phase 12 — Command Line Interface ✓ COMPLETE

### Goal

Provide tools for diagnostics and maintenance.

### Implementation

- Single entry point with subcommands (`mouseflow start`, `mouseflow status`, etc.)
- Service Layer exposing application capabilities as public API
- IPC via Unix sockets for CLI-daemon communication
- Commands: `start`, `status`, `devices`, `config show`, `config validate`, `config reload`
- Thread-safe configuration reload at runtime
- Comprehensive test coverage (unit + integration)

---

## Phase 13 — Release 1.0

### Goal

Publish the first stable release.

Possible distribution channels:

- PyPI
- AUR
- Source installation

---

## Phase 14 — Plugin API

### Goal

Allow third-party extensions.

Example:

plugins/

spotify.py

obsidian.py

---

# Definition of Done

A sprint is considered complete when:

- all acceptance criteria are satisfied
- tests pass
- lint passes
- type checking passes
- CI passes
- documentation is updated

Only then should the next sprint begin.
