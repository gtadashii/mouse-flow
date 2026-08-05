## Purpose

Manages the application lifecycle including startup, shutdown, signal handling, and operational interface exposure. The daemon coordinates component initialization, runs the event processing loop, and provides an IPC interface for CLI commands.

## ADDED Requirements

### Requirement: Daemon starts IPC server
The daemon SHALL start an IPC server in a separate thread during initialization to accept CLI commands.

#### Scenario: IPC server starts with daemon
- **WHEN** daemon initializes
- **THEN** IPC server is created
- **THEN** IPC server starts in separate thread
- **THEN** socket file is created at configured path
- **THEN** server listens for incoming connections

#### Scenario: IPC server uses service layer
- **WHEN** IPC server is created
- **THEN** server receives ApplicationServices instance
- **THEN** server dispatches commands to service methods

### Requirement: Daemon supports runtime configuration reload
The daemon SHALL support reloading configuration at runtime without restarting the process.

#### Scenario: Configuration reload updates state
- **WHEN** daemon receives reload command via IPC
- **WHEN** new configuration is valid
- **THEN** daemon parses new configuration
- **THEN** daemon updates internal configuration state
- **THEN** new configuration is used for subsequent event processing
- **THEN** event processing loop continues without interruption

#### Scenario: Configuration reload preserves state on failure
- **WHEN** daemon receives reload command via IPC
- **WHEN** new configuration is invalid
- **THEN** daemon does not update configuration state
- **THEN** daemon continues using previous configuration
- **THEN** error is returned to CLI

### Requirement: Daemon manages service layer instance
The daemon SHALL create and hold an ApplicationServices instance that wraps all components and exposes operational capabilities.

#### Scenario: Service layer created during initialization
- **WHEN** daemon initializes components
- **THEN** ApplicationServices instance is created
- **THEN** services receives references to all components
- **THEN** services is passed to IPC server

#### Scenario: Service layer has access to daemon state
- **WHEN** service methods need runtime state
- **THEN** services can access daemon state (active device, configuration, etc.)
- **THEN** services return current state information

### Requirement: Daemon handles graceful shutdown with IPC
The daemon SHALL gracefully shut down the IPC server during shutdown sequence.

#### Scenario: Graceful shutdown stops IPC server
- **WHEN** daemon receives shutdown signal
- **THEN** daemon stops accepting new IPC connections
- **THEN** daemon waits for active IPC requests to complete
- **THEN** daemon stops IPC server thread
- **THEN** daemon removes socket file
- **THEN** daemon continues with remaining shutdown sequence

### Requirement: Daemon entry point supports subcommands
The daemon SHALL be started via the `mouseflow start` subcommand rather than direct execution.

#### Scenario: Start via CLI subcommand
- **WHEN** user runs `mouseflow start`
- **THEN** CLI creates Daemon instance
- **THEN** CLI calls daemon.run()
- **THEN** daemon starts normally

### Requirement: Daemon maintains thread safety
The daemon SHALL ensure thread-safe access to shared state between event processing loop and IPC server thread.

#### Scenario: Configuration reload is thread-safe
- **WHEN** IPC thread processes reload command
- **WHEN** event processing thread is running
- **THEN** configuration update is atomic
- **THEN** no race conditions occur
- **THEN** both threads see consistent state

#### Scenario: State queries are thread-safe
- **WHEN** IPC thread queries daemon state
- **WHEN** event processing thread is modifying state
- **THEN** state access is synchronized
- **THEN** queries return consistent snapshots
