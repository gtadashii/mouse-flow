# ADR-004: Service Layer for Application Capabilities

## Status

Proposed

## Context

Sprint 12 introduces a Command Line Interface (CLI) that needs to access application capabilities such as:
- Listing available devices
- Showing loaded configuration
- Validating configuration files
- Reloading configuration at runtime
- Querying application status

Currently, these capabilities are embedded in individual components:
- `DeviceDiscovery` handles device detection
- `ConfigurationParser` handles configuration parsing
- `Daemon` manages lifecycle and holds runtime state

The CLI needs a clean API to access these capabilities without knowing about internal component implementations.

## Decision

Introduce a **Service Layer** that wraps existing components and exposes application capabilities as a public API.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Interface Layer                        │
│  ┌──────────┐              ┌──────────┐                │
│  │   CLI    │              │  Future  │                │
│  │          │              │   GUI    │                │
│  └────┬─────┘              └────┬─────┘                │
│       │                         │                       │
└───────┼─────────────────────────┼───────────────────────┘
        │                         │
        ▼                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Service Layer                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │              ApplicationServices                 │   │
│  │                                                  │   │
│  │  - list_devices() -> list[DeviceInfo]           │   │
│  │  - get_status() -> ApplicationStatus            │   │
│  │  - get_configuration() -> Configuration         │   │
│  │  - validate_configuration() -> ValidationResult │   │
│  │  - reload_configuration() -> ReloadResult       │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Component Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Device     │  │ Configuration│  │    Daemon    │  │
│  │  Discovery   │  │    Parser    │  │   (state)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Service API

```python
@dataclass(frozen=True)
class DeviceInfo:
    path: str
    name: str
    is_active: bool

@dataclass(frozen=True)
class ApplicationStatus:
    is_running: bool
    device_connected: bool
    configuration_loaded: bool
    active_profile: str | None = None

@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...] = ()

@dataclass(frozen=True)
class ReloadResult:
    success: bool
    message: str | None = None

class ApplicationServices:
    def __init__(
        self,
        discovery: DeviceDiscovery,
        parser: ConfigurationParser,
        daemon_state: DaemonState,
    ): ...
    
    def list_devices(self) -> list[DeviceInfo]:
        """List all supported mouse devices."""
        ...
    
    def get_status(self) -> ApplicationStatus:
        """Get current application status."""
        ...
    
    def get_configuration(self) -> Configuration:
        """Get currently loaded configuration."""
        ...
    
    def validate_configuration(self, path: Path) -> ValidationResult:
        """Validate configuration file without loading it."""
        ...
    
    def reload_configuration(self) -> ReloadResult:
        """Reload configuration from default path."""
        ...
```

## Alternatives Considered

### 1. Direct Component Access

CLI imports and uses components directly.

```python
# CLI code
from mouseflow.discovery import DeviceDiscovery
from mouseflow.parser import ConfigurationParser

discovery = DeviceDiscovery()
devices = discovery.find_devices()
```

**Pros:**
- Simpler, no additional layer
- Direct access to component capabilities

**Cons:**
- CLI coupled to component implementations
- Violates "CLI remains independent from business logic" (PRD requirement)
- Harder to change component interfaces without breaking CLI
- No centralized API for application capabilities
- Difficult to mock in CLI tests

**Why not chosen:** Violates separation of concerns and makes CLI dependent on internal implementations.

### 2. Facade Pattern

Single facade object that wraps all components.

```python
class ApplicationFacade:
    def __init__(self, discovery, parser, daemon): ...
    
    def list_devices(self) -> list[DeviceInfo]: ...
    def get_status(self) -> ApplicationStatus: ...
    # ... all methods in one class
```

**Pros:**
- Simple, single entry point
- Similar to service layer

**Cons:**
- Facade tends to become a "god object"
- Less explicit about service boundaries
- Harder to test individual services

**Why not chosen:** Service layer is more explicit and allows for better organization as capabilities grow.

### 3. Event-based Architecture

CLI publishes events, daemon subscribes and responds.

```python
# CLI
event_bus.publish("list_devices")
response = event_bus.wait_for_response()

# Daemon
event_bus.subscribe("list_devices", handler)
```

**Pros:**
- Fully decoupled
- Easy to add new consumers

**Cons:**
- Over-engineered for this use case
- Adds complexity (event bus, handlers, response tracking)
- Harder to understand flow
- Unnecessary for synchronous request/response

**Why not chosen:** Too complex for simple CLI commands. Service layer provides cleaner request/response pattern.

### 4. Command Pattern

Each command is a separate class with execute method.

```python
class ListDevicesCommand:
    def __init__(self, discovery): ...
    def execute(self) -> list[DeviceInfo]: ...

class GetStatusCommand:
    def __init__(self, daemon): ...
    def execute(self) -> ApplicationStatus: ...
```

**Pros:**
- Each command is isolated
- Easy to test
- Follows single responsibility

**Cons:**
- Many small classes (one per command)
- More boilerplate
- Harder to share state between commands

**Why not chosen:** Service layer provides similar benefits with less boilerplate. Can refactor to command pattern later if needed.

## Trade-offs

### Pros

1. **Separation of Concerns:** CLI only knows about service API, not component implementations
2. **Testability:** Services can be tested in isolation; CLI tests mock services
3. **Reusability:** Same API can be used by future interfaces (GUI, API, etc.)
4. **Flexibility:** Can change component implementations without affecting CLI
5. **Clarity:** Explicit API for application capabilities
6. **Dependency Inversion:** CLI depends on service abstraction, not component details

### Cons

1. **Additional Layer:** One more layer of indirection
2. **More Code:** Need to implement service classes and result objects
3. **Potential Duplication:** Services may wrap simple component calls
4. **Learning Curve:** New contributors need to understand service layer concept

## Consequences

### Positive

- CLI is independent of component implementations
- Easy to add new commands (add method to service layer)
- Services can combine multiple components for complex operations
- Clear API documentation (service methods)
- Easy to test CLI with mocked services
- Future interfaces (GUI, API) can reuse same services

### Negative

- Additional code to maintain (service layer, result objects)
- Slightly more complex flow (CLI → Service → Component)
- Need to define service boundaries and responsibilities

### Neutral

- Services are thin wrappers initially, but can evolve
- Result objects add type safety but also boilerplate
- Service layer can be split into multiple services as it grows

## Implementation

### Module Structure

```
src/mouseflow/
├── services.py          # ApplicationServices class
├── service_models.py    # DeviceInfo, ApplicationStatus, etc.
```

Or split into multiple service modules:

```
src/mouseflow/
├── services/
│   ├── __init__.py
│   ├── device_service.py
│   ├── config_service.py
│   └── status_service.py
```

**Recommendation:** Start with single `services.py` module. Split if it grows beyond ~300 lines.

### Service Implementation Example

```python
@dataclass(frozen=True)
class ApplicationServices:
    discovery: DeviceDiscovery
    parser: ConfigurationParser
    daemon_state: DaemonState
    
    def list_devices(self) -> list[DeviceInfo]:
        all_devices = self.discovery.find_all_supported_devices()
        active_device = self.daemon_state.active_device
        
        return [
            DeviceInfo(
                path=device.path,
                name=device.name,
                is_active=(device.path == active_device)
            )
            for device in all_devices
        ]
    
    def reload_configuration(self) -> ReloadResult:
        try:
            config_path = self.daemon_state.config_path
            new_config = self.parser.parse(config_path)
            self.daemon_state.update_configuration(new_config)
            return ReloadResult(success=True, message="Configuration reloaded")
        except Exception as e:
            return ReloadResult(success=False, message=str(e))
```

### Daemon Integration

Daemon creates and holds `ApplicationServices` instance:

```python
class Daemon:
    def __init__(self):
        self.services = ApplicationServices(
            discovery=self.discovery,
            parser=self.parser,
            daemon_state=self.state,
        )
        self.ipc_server = IPCServer(socket_path, self.services)
```

IPC server dispatches to services:

```python
class IPCServer:
    def _dispatch(self, request: dict) -> dict:
        command = request["command"]
        method = getattr(self.services, command)
        result = method(**request.get("args", {}))
        return {"status": "ok", "data": result}
```

## Related Decisions

- **ADR-003:** Unix socket IPC dispatches to service layer
- **ADR-005:** Single entry point CLI uses service layer via IPC

## References

- [Service Layer Pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Facade Pattern vs Service Layer](https://martinfowler.com/bliki/ServiceLayer.html)
- Project AGENTS.md: "Components communicate by exchanging domain objects"
