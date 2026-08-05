## Why

MouseFlow now operates as a background service (daemon mode), but users have no way to inspect its state, diagnose configuration issues, or perform operational tasks without directly accessing internal files or restarting the service. A command-line interface provides the operational visibility and control needed for a production-ready background service.

## What Changes

- Add a **Service Layer** that exposes application capabilities (device listing, configuration inspection, status queries, configuration reload) as a public API
- Add **IPC mechanism** (Unix socket) for communication between CLI and daemon processes
- Add **CLI component** with subcommands for operational tasks
- Modify **Daemon** to start IPC server and support runtime configuration reload
- Introduce **operational domain objects** (DeviceInfo, ApplicationStatus, ValidationResult, ReloadResult) for service layer responses
- Refactor entry point to support subcommands (`mouseflow start`, `mouseflow status`, etc.)

## Capabilities

### New Capabilities

- `cli-interface`: Command-line interface for inspecting and operating MouseFlow. Covers command parsing, subcommand routing, output formatting, and error handling.
- `service-layer`: Public API exposing application capabilities. Covers device queries, configuration inspection, validation, reload, and status reporting.
- `ipc-communication`: Inter-process communication between CLI and daemon. Covers Unix socket server/client, JSON protocol, request dispatching, and connection management.

### Modified Capabilities

- `daemon-lifecycle`: Daemon now starts IPC server in a separate thread and supports runtime configuration reload. Adds operational interface responsibility alongside lifecycle management.

## Impact

- **New modules**: `services.py`, `ipc.py`, `cli.py`
- **Modified modules**: `daemon.py` (IPC server, config reload), `domain.py` (operational objects)
- **Entry point**: Refactored to support subcommands via argparse
- **Dependencies**: No new external dependencies (uses stdlib: `socket`, `json`, `argparse`)
- **systemd service**: Updated to use `mouseflow start` instead of direct execution
- **Testing**: New test suites for service layer, IPC, and CLI components
- **Documentation**: Architecture docs updated with CLI, Service Layer, and IPC sections
