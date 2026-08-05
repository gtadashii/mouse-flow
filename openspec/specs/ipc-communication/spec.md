## Purpose

Enables communication between the CLI process and the daemon process using Unix domain sockets with a JSON message protocol, allowing CLI commands to query daemon state and trigger operations.

## Requirements

### Requirement: IPC uses Unix domain sockets
The system SHALL use Unix domain sockets for inter-process communication between CLI and daemon. The socket file SHALL be located at `~/.local/state/mouseflow/mouseflow.sock`.

#### Scenario: Socket file location
- **WHEN** daemon starts IPC server
- **THEN** socket file is created at `~/.local/state/mouseflow/mouseflow.sock`
- **THEN** parent directories are created if they do not exist

#### Scenario: Socket file cleanup on startup
- **WHEN** daemon starts IPC server
- **WHEN** socket file already exists from previous run
- **THEN** daemon removes stale socket file
- **THEN** daemon creates new socket file

### Requirement: IPC server runs in separate thread
The daemon SHALL start the IPC server in a separate thread to avoid blocking the event processing loop.

#### Scenario: IPC server does not block event loop
- **WHEN** daemon starts
- **THEN** IPC server runs in separate thread
- **THEN** event processing loop continues normally
- **THEN** daemon can handle both CLI requests and mouse events concurrently

### Requirement: IPC protocol uses JSON messages
The system SHALL use JSON for message serialization. Requests and responses SHALL follow a defined schema.

#### Scenario: Request format
- **WHEN** CLI sends command request
- **THEN** request is JSON object with "command" field (string)
- **THEN** request has optional "args" field (object)
- **THEN** request is valid JSON

#### Scenario: Success response format
- **WHEN** daemon processes command successfully
- **THEN** response is JSON object with "status" field set to "ok"
- **THEN** response has "data" field containing result
- **THEN** response is valid JSON

#### Scenario: Error response format
- **WHEN** daemon encounters error processing command
- **THEN** response is JSON object with "status" field set to "error"
- **THEN** response has "message" field containing error description
- **THEN** response is valid JSON

### Requirement: IPC server dispatches to service layer
The IPC server SHALL dispatch incoming commands to the appropriate Service Layer method based on the command name.

#### Scenario: Dispatch devices command
- **WHEN** IPC server receives request with command="devices"
- **THEN** server calls ApplicationServices.list_devices()
- **THEN** server serializes result to JSON
- **THEN** server sends response to CLI

#### Scenario: Dispatch status command
- **WHEN** IPC server receives request with command="status"
- **THEN** server calls ApplicationServices.get_status()
- **THEN** server serializes result to JSON
- **THEN** server sends response to CLI

#### Scenario: Dispatch unknown command
- **WHEN** IPC server receives request with unknown command
- **THEN** server returns error response
- **THEN** error message indicates unknown command

### Requirement: IPC client connects to daemon socket
The CLI SHALL connect to the daemon's Unix socket to send commands and receive responses.

#### Scenario: Successful connection
- **WHEN** CLI sends command
- **WHEN** daemon is running and socket exists
- **THEN** CLI connects to socket
- **THEN** CLI sends JSON request
- **THEN** CLI receives JSON response
- **THEN** CLI closes connection

#### Scenario: Daemon not running
- **WHEN** CLI sends command
- **WHEN** daemon is not running
- **THEN** CLI detects connection error
- **THEN** CLI displays "Error: MouseFlow daemon is not running"
- **THEN** CLI exits with non-zero status

#### Scenario: Socket file does not exist
- **WHEN** CLI sends command
- **WHEN** socket file does not exist
- **THEN** CLI detects missing socket
- **THEN** CLI displays appropriate error message
- **THEN** CLI exits with non-zero status

### Requirement: IPC handles concurrent connections
The IPC server SHALL handle multiple simultaneous CLI invocations without blocking or data corruption.

#### Scenario: Multiple concurrent CLI commands
- **WHEN** multiple CLI processes send commands simultaneously
- **THEN** IPC server handles each connection in separate thread
- **THEN** each request is processed independently
- **THEN** responses are sent to correct clients
- **THEN** no data corruption occurs

### Requirement: IPC server lifecycle management
The IPC server SHALL be started when daemon starts and stopped when daemon shuts down, with proper cleanup of socket file.

#### Scenario: Server starts with daemon
- **WHEN** daemon starts
- **THEN** IPC server is started
- **THEN** socket file is created
- **THEN** server listens for connections

#### Scenario: Server stops with daemon
- **WHEN** daemon receives shutdown signal
- **THEN** IPC server is stopped
- **THEN** socket file is removed
- **THEN** server thread is terminated

#### Scenario: Graceful shutdown with active connections
- **WHEN** daemon receives shutdown signal
- **WHEN** CLI connections are active
- **THEN** daemon waits for active requests to complete
- **THEN** daemon stops accepting new connections
- **THEN** daemon cleans up socket file

### Requirement: IPC uses stdlib only
The IPC implementation SHALL use only Python standard library modules (`socket`, `json`, `threading`) without external dependencies.

#### Scenario: No external dependencies
- **WHEN** IPC module is imported
- **THEN** only stdlib modules are used
- **THEN** no external packages are required

### Requirement: IPC serializes domain objects
The IPC server SHALL serialize domain objects and operational objects to JSON for transmission to CLI.

#### Scenario: Serialize DeviceInfo list
- **WHEN** service returns list of DeviceInfo objects
- **THEN** IPC server converts to JSON array
- **THEN** each DeviceInfo becomes JSON object with path, name, is_active fields
- **THEN** JSON is valid and parseable

#### Scenario: Serialize ApplicationStatus
- **WHEN** service returns ApplicationStatus object
- **THEN** IPC server converts to JSON object
- **THEN** all fields are included in JSON
- **THEN** JSON is valid and parseable

### Requirement: IPC handles serialization errors
The IPC server SHALL handle serialization errors gracefully and return appropriate error responses.

#### Scenario: Serialization failure
- **WHEN** IPC server cannot serialize result to JSON
- **THEN** server returns error response
- **THEN** error message indicates serialization failure
- **THEN** daemon continues running
