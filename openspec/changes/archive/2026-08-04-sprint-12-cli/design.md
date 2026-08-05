## Context

MouseFlow currently runs as a daemon (Sprint 11) with all lifecycle management in place. The application processes mouse events through a pipeline but has no operational interface for users to inspect state or perform maintenance tasks.

Current architecture:
- Single entry point (`__main__.py`) that creates and runs Daemon
- Daemon orchestrates components: DeviceDiscovery, ConfigurationParser, EventDispatcher, ProfileResolver, ActionRunner
- Configuration loaded once at startup, not reloadable
- No inter-process communication mechanism

Constraints:
- Must use stdlib only (no external CLI frameworks, no IPC libraries)
- Must maintain existing event processing pipeline unchanged
- Must support systemd service integration
- Must be testable in isolation

See `proposal.md` for motivation and `specs/` for detailed requirements.

## Goals / Non-Goals

**Goals:**
- Provide CLI for operational commands (status, devices, config inspection/reload)
- Enable runtime configuration reload without daemon restart
- Maintain clean separation between CLI, IPC, Service Layer, and Daemon
- Use only Python stdlib (argparse, socket, json, threading)
- Ensure thread safety between event loop and IPC server
- Keep existing event processing pipeline unchanged

**Non-Goals:**
- Configuration editing via CLI (out of scope for Sprint 12)
- GUI interface (future work, but Service Layer will support it)
- Remote management (CLI is local-only)
- Interactive shell or REPL
- Plugin management
- Breaking changes to existing components

## Decisions

### 1. Single Entry Point with Subcommands

**Decision:** Use single `mouseflow` binary with subcommands (`start`, `status`, `devices`, `config *`).

**Rationale:**
- More intuitive for users (one command to learn)
- Follows common CLI patterns (git, docker, kubectl)
- Easier to package and distribute
- `--help` provides discoverability

**Alternatives considered:**
- Separate binaries (`mouseflow` for daemon, `mouseflow-cli` for CLI): More confusing, harder to document
- Environment variable mode: Non-standard, poor UX
- Automatic mode detection: Ambiguous, limits extensibility

**Trade-offs:**
- CLI module handles both daemon startup and IPC communication
- Need to distinguish "local" commands (start) from "remote" commands (status, devices)

### 2. Unix Domain Sockets for IPC

**Decision:** Use Unix domain sockets with JSON message protocol.

**Rationale:**
- stdlib support (`socket`, `json` modules)
- Fast, low overhead for local communication
- Natural request/response pattern
- Works well with systemd
- Secure (file permissions control access)

**Alternatives considered:**
- D-Bus: Requires external library, overkill for this use case
- Signal-based: Cannot return data, only trigger actions
- File-based: Race conditions, stale data, polling required
- HTTP/REST: Overhead for local IPC, requires HTTP server

**Trade-offs:**
- Need to manage socket file lifecycle (creation, cleanup)
- Must handle concurrent connections
- Socket path must be consistent between daemon and CLI

**Socket location:** `~/.local/state/mouseflow/mouseflow.sock` (follows XDG Base Directory Specification)

### 3. Service Layer Pattern

**Decision:** Introduce Service Layer that wraps components and exposes capabilities as public API.

**Rationale:**
- Clean separation between interface (CLI) and implementation (components)
- Reusable API for future interfaces (GUI, API)
- Testable in isolation with mocked components
- Follows dependency inversion principle

**Alternatives considered:**
- Direct component access: Couples CLI to implementations, violates separation of concerns
- Facade pattern: Similar but less explicit about service boundaries
- Event-based: Over-engineered for synchronous request/response
- Command pattern: More boilerplate, similar benefits

**Trade-offs:**
- Additional layer of indirection
- More code to maintain (service classes, result objects)
- Services may be thin wrappers initially

**Service API:**
```python
class ApplicationServices:
    def list_devices() -> list[DeviceInfo]
    def get_status() -> ApplicationStatus
    def get_configuration() -> Configuration
    def validate_configuration(path) -> ValidationResult
    def reload_configuration() -> ReloadResult
```

### 4. Operational Domain Objects

**Decision:** Create frozen dataclasses for operational results (DeviceInfo, ApplicationStatus, ValidationResult, ReloadResult).

**Rationale:**
- Consistent with existing domain model (immutable dataclasses)
- Type-safe and self-documenting
- Easy to serialize to JSON for IPC
- Testable in isolation

**Alternatives considered:**
- Return raw dicts: Not type-safe, harder to test
- Return component objects directly: Couples Service Layer to component internals
- Use existing domain objects only: Insufficient for operational results

**Trade-offs:**
- More classes to define
- Need serialization logic for IPC

### 5. IPC Server in Separate Thread

**Decision:** Run IPC server in a daemon thread alongside event processing loop.

**Rationale:**
- Simple concurrency model
- Shares state directly (no IPC between threads)
- Daemon thread automatically cleaned up on shutdown

**Alternatives considered:**
- Separate process for IPC: More complex, requires IPC between processes
- AsyncIO: Adds complexity, generator-based pipeline works correctly
- Multiprocessing: Overkill, shared state is sufficient

**Trade-offs:**
- Need thread safety for shared state (configuration reload)
- Daemon thread doesn't block shutdown
- Must handle concurrent CLI connections

**Thread safety approach:**
- Use `threading.Lock` for configuration updates
- Configuration reload is atomic (parse new, swap reference)
- State queries return consistent snapshots

### 6. Configuration Reload Strategy

**Decision:** Full reload - re-parse configuration file and replace Configuration object.

**Rationale:**
- Simple to implement and reason about
- No need to track incremental changes
- Consistent with "load once at startup" model
- Easy to test

**Alternatives considered:**
- Hot reload (incremental updates): Complex, need to track changes
- Restart daemon: Disrupts event processing, poor UX

**Trade-offs:**
- Brief moment where old and new configuration coexist
- Need to ensure thread-safe swap
- Invalid configuration leaves old config in place

**Implementation:**
```python
def reload_configuration(self) -> ReloadResult:
    with self._config_lock:
        try:
            new_config = self.parser.parse(self.config_path)
            self._configuration = new_config
            return ReloadResult(success=True)
        except Exception as e:
            return ReloadResult(success=False, message=str(e))
```

### 7. CLI Framework

**Decision:** Use `argparse` from stdlib.

**Rationale:**
- No external dependencies
- Sufficient for subcommand structure
- Well-documented, widely used
- Supports nested subcommands (`config show`, `config validate`)

**Alternatives considered:**
- click: External dependency, more expressive but not necessary
- typer: External dependency, type hints nice-to-have

**Trade-offs:**
- More verbose than click/typer
- Manual output formatting
- Adequate for this use case

### 8. Module Structure

**Decision:** Create three new modules: `services.py`, `ipc.py`, `cli.py`.

**Rationale:**
- Clear separation of concerns
- Each module has single responsibility
- Easy to test in isolation
- Follows existing project structure

**Alternatives considered:**
- Single `cli` package with multiple modules: Over-engineering for initial implementation
- Add to existing modules: Mixes concerns, harder to understand

**Module responsibilities:**
- `services.py`: ApplicationServices class, operational domain objects
- `ipc.py`: IPCServer, IPCClient, JSON protocol handling
- `cli.py`: Argument parsing, command routing, output formatting

**Trade-offs:**
- Three new files to maintain
- Clear boundaries justify the split

## Risks / Trade-offs

### Risk: Thread Safety Issues
**Risk:** Race conditions between event processing loop and IPC server thread during configuration reload.

**Mitigation:**
- Use `threading.Lock` for configuration updates
- Atomic swap (parse new, assign reference)
- Test with concurrent access scenarios
- Keep critical section small

### Risk: Socket File Leaks
**Risk:** Socket file not cleaned up on crash or improper shutdown.

**Mitigation:**
- Check and remove stale socket on startup
- Use try/finally for cleanup
- Handle signals gracefully
- Document socket location for manual cleanup if needed

### Risk: IPC Protocol Evolution
**Risk:** JSON protocol changes break compatibility between CLI and daemon versions.

**Mitigation:**
- Keep protocol simple initially
- Add version field if needed (future)
- CLI and daemon are updated together (same package)
- Document protocol clearly

### Risk: Service Layer Complexity
**Risk:** Service Layer becomes bloated as more capabilities are added.

**Mitigation:**
- Start with single `services.py` module
- Split into multiple services if it grows beyond ~300 lines
- Keep services thin (delegate to components)
- Clear API boundaries

### Risk: Daemon Startup Time
**Risk:** IPC server initialization adds delay to daemon startup.

**Mitigation:**
- Socket creation is fast (local filesystem)
- Server starts in background thread
- No blocking of event processing loop
- Acceptable trade-off for operational capability

### Trade-off: Simplicity vs Extensibility
**Trade-off:** Current design is simple but may need refactoring for advanced features (remote management, GUI).

**Mitigation:**
- Service Layer provides clean API for future interfaces
- IPC protocol can be extended (add versioning if needed)
- Unix socket can be replaced with HTTP/REST if remote access needed
- Simple now, extensible later

### Trade-off: Thread Safety vs Performance
**Trade-off:** Locking for configuration reload adds overhead.

**Mitigation:**
- Lock held only during configuration swap (microseconds)
- No locking for read-only state queries
- Acceptable trade-off for correctness
- Configuration reload is rare operation

## Migration Plan

### Deployment Steps

1. **Update entry point**
   - Refactor `__main__.py` to use CLI with subcommands
   - `mouseflow start` replaces direct daemon execution
   - Maintain backward compatibility during transition (if needed)

2. **Update systemd service**
   - Change `ExecStart` to `mouseflow start`
   - Test service startup/shutdown
   - Verify signal handling still works

3. **Deploy new version**
   - Install updated package
   - Restart systemd service (`systemctl --user restart mouseflow`)
   - Verify daemon starts correctly
   - Test CLI commands

4. **Verify functionality**
   - Run `mouseflow status` to verify IPC
   - Run `mouseflow devices` to verify service layer
   - Run `mouseflow config reload` to verify reload
   - Check logs for errors

### Rollback Strategy

If issues arise:
1. Stop daemon: `systemctl --user stop mouseflow`
2. Revert to previous version: `uv pip install mouseflow==<previous>`
3. Update systemd service to use old entry point (if changed)
4. Start daemon: `systemctl --user start mouseflow`

Rollback is straightforward since:
- No database migrations
- No configuration format changes
- Event processing pipeline unchanged
- CLI is additive (doesn't break existing functionality)

### Backward Compatibility

- Existing configuration files work unchanged
- Event processing behavior unchanged
- systemd service requires update (ExecStart change)
- No breaking changes to public APIs (domain objects)

## Open Questions

None at this time. All critical decisions have been resolved:
- IPC mechanism: Unix socket (decided)
- CLI framework: argparse (decided)
- Service Layer: Yes (decided)
- Configuration reload: Full reload (decided)
- Entry point structure: Single with subcommands (decided)
