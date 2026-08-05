# ADR-003: Unix Socket for CLI-Daemon Communication

## Status

Proposed

## Context

Sprint 12 introduces a Command Line Interface (CLI) that needs to communicate with the running MouseFlow daemon. The daemon runs as a background systemd service, while CLI commands are executed as separate processes.

The CLI needs to:
- Query runtime state (status, devices, configuration)
- Trigger operations (reload configuration)
- Receive structured responses from the daemon

This requires an inter-process communication (IPC) mechanism between the CLI and daemon processes.

## Decision

Use **Unix domain sockets** with a JSON message protocol for CLI-daemon communication.

### Architecture

```
┌─────────────────┐
│   CLI Process   │
│                 │
│  1. Parse args  │
│  2. Connect     │
│  3. Send JSON   │
│  4. Receive     │
│  5. Display     │
└────────┬────────┘
         │ Unix Socket
         │ (JSON messages)
         ▼
┌─────────────────┐
│  Daemon Process │
│                 │
│  Socket Server  │
│  (thread)       │
│       │         │
│       ▼         │
│  Service Layer  │
└─────────────────┘
```

### Protocol

**Request format:**
```json
{
  "command": "devices",
  "args": {}
}
```

**Response format:**
```json
{
  "status": "ok",
  "data": {
    "devices": [...]
  }
}
```

**Error response:**
```json
{
  "status": "error",
  "message": "Configuration file not found"
}
```

### Socket Location

Socket file: `~/.local/state/mouseflow/mouseflow.sock`

This follows XDG Base Directory Specification for state files.

## Alternatives Considered

### 1. D-Bus

Standard IPC mechanism for Linux desktop applications.

**Pros:**
- Built-in service discovery
- Standard for Linux desktop
- Integrates with systemd

**Cons:**
- Requires external library (`dasbus` or similar)
- More complex setup and configuration
- Overkill for simple request/response pattern
- Adds dependency (violates "prefer standard library")

**Why not chosen:** Unix sockets provide the same capability with stdlib only, simpler setup, and no external dependencies.

### 2. Signal-based Communication

Use POSIX signals (SIGUSR1, SIGUSR2) to trigger actions.

**Pros:**
- Very simple implementation
- No socket management
- Works with existing signal handlers

**Cons:**
- Cannot return data (only trigger actions)
- Not suitable for inspection commands (status, devices, config)
- Limited to fire-and-forget operations
- No structured error reporting

**Why not chosen:** CLI needs to receive structured data (device lists, configuration, status), not just trigger actions.

### 3. File-based Communication

Daemon writes state to files, CLI reads them.

**Pros:**
- Simple concept
- No socket management
- State persists across daemon restarts

**Cons:**
- Race conditions (concurrent read/write)
- Requires polling for real-time updates
- Slow for interactive commands
- Stale data issues
- File locking complexity

**Why not chosen:** Race conditions and stale data make this unreliable for interactive CLI commands.

### 4. HTTP/REST API

Expose daemon as HTTP server.

**Pros:**
- Well-understood protocol
- Easy to test with curl
- Can support remote management (future)

**Cons:**
- HTTP overhead for local IPC
- Requires HTTP server library
- Overkill for local-only communication
- Security considerations (port binding)
- More complex than Unix sockets

**Why not chosen:** Unix sockets are simpler, faster, and sufficient for local-only communication. HTTP is overkill for this use case.

### 5. Named Pipes (FIFO)

Use named pipes for communication.

**Pros:**
- Simple concept
- stdlib support
- No network overhead

**Cons:**
- Unidirectional by default (need two pipes)
- More complex than sockets for request/response
- Limited concurrency support
- Harder to handle multiple simultaneous requests

**Why not chosen:** Unix sockets provide bidirectional communication and better concurrency support with similar complexity.

## Trade-offs

### Pros

1. **Standard Library:** Uses Python `socket` module, no external dependencies
2. **Simple:** Straightforward request/response pattern
3. **Fast:** Low overhead, local communication only
4. **Secure:** File permissions control access
5. **Systemd-friendly:** Works well with systemd service management
6. **Testable:** Can mock socket communication in tests
7. **Extensible:** Easy to add new commands without protocol changes

### Cons

1. **Socket Management:** Need to create/cleanup socket file
2. **Concurrent Connections:** Must handle multiple CLI invocations
3. **Not Discoverable:** CLI must know socket path (solved by convention)
4. **Daemon Required:** CLI fails if daemon not running (acceptable for operational commands)

## Consequences

### Positive

- CLI can query daemon state in real-time
- Structured error reporting
- Clean separation between CLI and daemon
- Easy to extend with new commands
- No external dependencies
- Works well with systemd

### Negative

- Socket file lifecycle management (creation, cleanup)
- Need to handle daemon not running (connection refused)
- Thread safety in daemon (socket server runs in separate thread)
- Socket path must be consistent between daemon and CLI

### Neutral

- JSON protocol adds minimal overhead
- Socket path follows XDG convention
- Existing daemon architecture unchanged (socket server added as new responsibility)

## Implementation

### Daemon Side

```python
import socket
import json
import threading
from pathlib import Path

class IPCServer:
    def __init__(self, socket_path: Path, services: ServiceLayer):
        self.socket_path = socket_path
        self.services = services
        self._server_socket: socket.socket | None = None
        self._running = False
    
    def start(self) -> None:
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        if self.socket_path.exists():
            self.socket_path.unlink()
        
        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_socket.bind(str(self.socket_path))
        self._server_socket.listen(5)
        self._running = True
        
        thread = threading.Thread(target=self._accept_loop, daemon=True)
        thread.start()
    
    def _accept_loop(self) -> None:
        while self._running:
            conn, _ = self._server_socket.accept()
            threading.Thread(
                target=self._handle_connection,
                args=(conn,),
                daemon=True
            ).start()
    
    def _handle_connection(self, conn: socket.socket) -> None:
        try:
            data = conn.recv(4096)
            request = json.loads(data)
            response = self._dispatch(request)
            conn.sendall(json.dumps(response).encode())
        finally:
            conn.close()
    
    def _dispatch(self, request: dict) -> dict:
        command = request["command"]
        args = request.get("args", {})
        
        try:
            result = self.services.execute(command, **args)
            return {"status": "ok", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def stop(self) -> None:
        self._running = False
        if self._server_socket:
            self._server_socket.close()
        if self.socket_path.exists():
            self.socket_path.unlink()
```

### CLI Side

```python
import socket
import json
from pathlib import Path

class IPCClient:
    def __init__(self, socket_path: Path):
        self.socket_path = socket_path
    
    def send_command(self, command: str, args: dict | None = None) -> dict:
        if not self.socket_path.exists():
            raise ConnectionError("Daemon not running")
        
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(str(self.socket_path))
            request = {"command": command, "args": args or {}}
            sock.sendall(json.dumps(request).encode())
            
            data = sock.recv(4096)
            return json.loads(data)
        finally:
            sock.close()
```

## Related Decisions

- **ADR-002:** Daemon component manages lifecycle; IPC server is added as a daemon responsibility
- **ADR-004:** Service layer provides the API that IPC dispatches to

## References

- [Unix Domain Sockets Tutorial](https://man7.org/linux/man-pages/man7/unix.7.html)
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- Project AGENTS.md: "Prefer the standard library unless there is a compelling reason not to"
