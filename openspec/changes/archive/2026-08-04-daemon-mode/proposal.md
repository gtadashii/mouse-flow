## Why

MouseFlow currently runs as a manually executed command-line program that terminates when the user stops it. This creates friction and prevents seamless integration with the user's desktop session. A daemon mode is needed to provide continuous mouse customization as a background service that starts automatically and manages its lifecycle gracefully.

## What Changes

- **New daemon lifecycle component**: A dedicated `daemon.py` module responsible for application startup, shutdown orchestration, and signal handling (SIGTERM, SIGINT).
- **Logging infrastructure**: Replace all `print()` statements with Python's stdlib `logging` module for proper observability in long-running execution.
- **Graceful shutdown**: Ensure all resources (evdev device, i3ipc connection) are released cleanly when the application terminates.
- **systemd user service**: Provide a service unit file for automatic startup with the user session via `systemctl --user`.
- **Entry point refactoring**: `__main__.py` becomes a thin entry point that delegates lifecycle management to the daemon component.

## Capabilities

### New Capabilities

- `daemon-lifecycle`: Covers the daemon component for application lifecycle management, including startup orchestration, signal handling, graceful shutdown, logging infrastructure, and systemd service integration.

### Modified Capabilities

None. The existing pipeline capabilities (device-discovery, input-engine, event-dispatcher, etc.) maintain their requirements unchanged. The daemon layer wraps the pipeline without modifying its behavior.

## Impact

- **New code**: `src/mouseflow/daemon.py` (lifecycle orchestration)
- **Modified code**: All modules with `print()` calls (`__main__.py`, `discovery.py`, `dispatcher.py`, `loader.py`, `runner.py`) will use logging instead
- **New infrastructure**: `packaging/mouseflow.service` (systemd user service unit)
- **Documentation**: `docs/architecture.md` updated with daemon component
- **Dependencies**: No new external dependencies (uses stdlib `signal` and `logging`)
