# ADR 002: Daemon Lifecycle as Separate Component

## Status

Accepted

## Context

MouseFlow was initially implemented as a simple command-line program with all lifecycle logic in `__main__.py`. As the project evolved, the need for background execution as a systemd service became apparent (Sprint 11 - Daemon Mode).

The `__main__.py` file was mixing multiple concerns:
- Device discovery
- Configuration loading
- Component initialization
- Event loop execution
- Action processing

This made it difficult to:
- Test lifecycle behavior in isolation
- Implement graceful shutdown
- Handle signals properly
- Integrate with systemd

## Decision

Create a dedicated `daemon.py` module as a separate lifecycle component that:
- Orchestrates application startup (initialization order)
- Manages the event processing loop
- Handles OS signals (SIGTERM, SIGINT) for graceful shutdown
- Coordinates resource cleanup via try/finally blocks
- Configures logging infrastructure

The `__main__.py` becomes a thin entry point that simply creates a `Daemon` instance and calls `run()`.

## Alternatives Considered

### 1. Expand `__main__.py`
Add lifecycle management directly to the existing entry point.

**Rejected:** Would mix entry point with lifecycle management, violating single responsibility principle. Harder to test.

### 2. Use a daemon framework/library
Use python-daemon or similar library for daemonization.

**Rejected:** Unnecessary external dependency for a straightforward lifecycle. The stdlib provides all needed functionality (signal, logging).

### 3. Use async/asyncio
Implement the event loop using asyncio for better signal handling and cancellation.

**Rejected:** The generator-based pipeline works correctly for continuous processing. Async adds complexity without clear benefit for this use case.

### 4. Use atexit for cleanup
Register cleanup functions with the atexit module.

**Rejected:** Less explicit than try/finally blocks. Harder to test and reason about cleanup order.

## Consequences

### Positive
- Clear separation of lifecycle management from business logic
- Testable lifecycle in isolation (27 unit tests for daemon)
- Follows existing pattern of single-responsibility components
- Graceful shutdown with proper resource cleanup
- Signal handling for SIGTERM/SIGINT
- systemd integration via simple service unit
- Structured logging for daemon-appropriate observability

### Negative
- One more module to maintain (justified by PRD requirement)
- Slightly more complex startup sequence

### Neutral
- No new external dependencies (uses stdlib signal and logging)
- Existing pipeline unchanged (daemon wraps it)

## Implementation

The `Daemon` class in `src/mouseflow/daemon.py` provides:
- `__init__`: Accepts optional dependencies for testing
- `_initialize`: Sets up all components in order
- `_shutdown`: Graceful cleanup
- `_handle_signal`: Signal handler for SIGTERM/SIGINT
- `_register_signal_handlers`: Registers signal handlers
- `_run_event_loop`: Main event processing loop
- `run`: Public entry point that orchestrates everything

The systemd service unit at `packaging/mouseflow.service` uses `Type=simple` since the application doesn't fork.
