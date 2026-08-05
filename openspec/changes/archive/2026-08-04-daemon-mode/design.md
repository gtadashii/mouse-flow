## Context

See proposal.md for motivation. The current application runs as a synchronous command-line program with a simple event loop in `__main__.py`. There is no lifecycle management, signal handling, or structured logging. The architecture follows a pipeline pattern where domain objects flow through transformation stages.

## Goals / Non-Goals

**Goals:**

- Introduce a daemon lifecycle layer that wraps the existing pipeline without modifying it
- Provide graceful startup and shutdown with proper resource cleanup
- Enable systemd user service integration
- Replace `print()` with logging for daemon-appropriate observability
- Keep the implementation simple and testable

**Non-Goals:**

- Modifying the input processing pipeline (it works correctly as-is)
- Adding configuration reload at runtime (future work)
- Implementing a CLI for diagnostics (Sprint 12)
- Supporting multiple instances or IPC between processes
- Adding async/asyncio (generator-based approach is sufficient)

## Decisions

### Decision 1: Separate daemon component

**Choice:** Create `src/mouseflow/daemon.py` as a dedicated lifecycle component.

**Rationale:** The PRD explicitly requires separation between lifecycle management and business logic. The current `__main__.py` mixes concerns (discovery, config, event loop, action execution). A dedicated daemon module follows the single-responsibility principle and makes lifecycle testable in isolation.

**Alternatives considered:**

- *Expand `__main__.py`*: Rejected — would mix entry point with lifecycle, violating separation of concerns.
- *Use a daemon framework/library*: Rejected — unnecessary external dependency for a straightforward lifecycle.
- *Use async/asyncio*: Rejected — the generator-based pipeline works fine; async adds complexity without clear benefit.

### Decision 2: stdlib logging over print()

**Choice:** Replace all `print()` calls with Python's `logging` module.

**Rationale:** Print statements lack severity levels, formatting control, and integration with systemd journal. The stdlib `logging` module provides all necessary features without external dependencies.

**Alternatives considered:**

- *Keep print() and redirect stdout*: Rejected — no severity levels, poor systemd journal integration.
- *Use structlog or loguru*: Rejected — external dependencies for features stdlib handles adequately.

### Decision 3: Signal handling via stdlib signal module

**Choice:** Register handlers for SIGTERM and SIGINT in the daemon component using Python's `signal` module.

**Rationale:** Standard POSIX signal handling is sufficient for graceful shutdown. The daemon sets a shutdown flag or raises `SystemExit` to trigger cleanup.

**Alternatives considered:**

- *Rely on process termination*: Rejected — doesn't guarantee resource cleanup.
- *Use asyncio for cancellation*: Rejected — over-engineering for current generator-based design.

### Decision 4: Context managers for resource cleanup

**Choice:** Use context managers (`with` statements) or explicit `try/finally` blocks to ensure resources are released.

**Rationale:** Context managers provide Pythonic, exception-safe resource management. The evdev device and i3ipc connection should be wrapped to guarantee cleanup.

**Alternatives considered:**

- *Manual cleanup in shutdown handler*: Rejected — error-prone,容易遗漏 edge cases.
- *Use atexit module*: Rejected — less explicit than context managers, harder to test.

### Decision 5: systemd Type=simple service

**Choice:** Use `Type=simple` in the systemd service unit.

**Rationale:** The application doesn't fork or daemonize itself. systemd manages the process directly. This is the simplest and most appropriate service type.

**Alternatives considered:**

- *Type=notify*: Rejected — requires sd_notify integration, unnecessary complexity.
- *Type=forking*: Rejected — application doesn't fork.
- *Type=oneshot*: Rejected — application is long-running, not a one-time task.

### Decision 6: Logging configuration at daemon startup

**Choice:** Configure logging once in the daemon component before starting the pipeline.

**Rationale:** Centralized logging configuration ensures consistent formatting and levels across all modules. Modules use `logging.getLogger(__name__)` for module-level loggers.

**Alternatives considered:**

- *Configure logging in each module*: Rejected — decentralized, inconsistent.
- *Pass logger instances to components*: Rejected — unnecessary coupling, stdlib pattern is sufficient.

## Risks / Trade-offs

**[Risk] Startup ordering complexity** → Mitigation: Document initialization order clearly in daemon component. Test startup sequence explicitly.

**[Risk] Resource leaks on unexpected errors** → Mitigation: Use context managers consistently. Test shutdown under various failure scenarios.

**[Risk] Signal handling conflicts with evdev event loop** → Mitigation: Signals are handled at Python level, not in evdev. Test signal delivery during event processing.

**[Trade-off] No hot-reload of configuration** → Acceptable for Sprint 11. Future sprints can add this without architectural changes.

**[Trade-off] Logging replaces user-visible print output** → Acceptable. Logging to stderr is standard for daemons. systemd journal captures logs automatically.

**[Trade-off] No IPC mechanism for CLI integration** → Acceptable. Sprint 12 (CLI) will need to add this, but it's independent of daemon lifecycle.
