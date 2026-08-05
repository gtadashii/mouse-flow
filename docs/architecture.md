# MouseFlow Architecture

This document describes the current architecture of MouseFlow, explaining how the system is organized and how data flows through the application.

---

## Architectural Vision

MouseFlow is designed as a **pipeline of domain object transformations**. Each component has a single responsibility: it receives domain objects (or raw data), performs one transformation, and produces domain objects for the next stage.

This architecture ensures:
- **Separation of concerns**: Each component does one thing well
- **Testability**: Components can be tested in isolation with mock inputs
- **Extensibility**: New features can be added as new pipeline stages
- **Maintainability**: Changes are localized to specific stages

---

## Pipeline Overview

```
┌─────────────────┐
│  Raw Device     │
│  Event (evdev)  │
└────────┬────────┘
           │
           ▼
┌─────────────────┐
│ Device Discovery│ ← Selects supported mouse device
└────────┬────────┘
           │
           ▼
┌─────────────────┐
│  Input Engine   │ ← Converts raw events to UserInput
│                 │   (includes GestureRecognizer)
└────────┬────────┘
           │ UserInput
           ▼
┌─────────────────┐
│     Event       │ ← Combines event + window context
│   Dispatcher    │
└────────┬────────┘
           │ DispatchContext
           ▼
┌─────────────────┐
│    Profile      │ ← Selects appropriate profile
│   Resolver      │   (application-specific or global)
└────────┬────────┘
           │ Profile | None
           ▼
┌─────────────────┐
│ Configuration   │ ← Resolves action from selected Profile
│    Loader       │
└────────┬────────┘
           │ Action
           ▼
┌─────────────────┐
│  Action Runner  │ ← Orchestrates action execution
│                 │
│  ┌───────────┐  │
│  │ Keyboard  │  │
│  │  Adapter  │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │   Shell   │  │
│  │  Adapter  │  │
│  └───────────┘  │
└────────┬────────┘
           │ ExecutionResult
           ▼
┌─────────────────┐
│    Reporting    │ ← Formats and displays results
└─────────────────┘
```

Each arrow represents a domain object being passed from one component to the next. Infrastructure details (evdev, i3ipc, file I/O) are confined to the edges and never leak into the domain.

### Configuration Loading (Startup)

Configuration is loaded once at startup, before event processing begins:

```
┌─────────────────┐
│  config.yaml    │ ← User-defined configuration file
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Configuration   │ ← Parses YAML, validates, translates to domain
│    Parser       │
└────────┬────────┘
         │ Configuration
         ▼
┌─────────────────┐
│   Application   │ ← Uses Configuration for action resolution
│     Runtime     │
└─────────────────┘
```

The Configuration Parser is the only component that knows about the YAML format. After startup, the entire application operates on domain objects exclusively.

### CLI Command Flow (Sprint 12)

The CLI provides operational commands that interact with the running daemon:

```
┌─────────────────┐
│   User Command  │
│  (mouseflow X)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      CLI        │ ← Parses command, validates args
└────────┬────────┘
         │ IPC Request (JSON)
         ▼
┌─────────────────┐
│   Unix Socket   │ ← IPC mechanism (stdlib socket)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IPC Server     │ ← Daemon thread, dispatches to services
│   (thread)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Service      │ ← Wraps components, exposes capabilities
│     Layer       │
└────────┬────────┘
         │ Result (domain or operational objects)
         ▼
┌─────────────────┐
│   CLI Output    │ ← Formats and displays result
└─────────────────┘
```

The CLI operates independently of the event processing pipeline. It queries the daemon's runtime state without interfering with mouse event processing.

---

## Components

### Device Discovery

**Responsibility:** Detect and select a supported mouse device.

**Input:** System device list (`/dev/input/event*`)

**Output:** Selected `InputDevice` path

**Key behaviors:**
- Enumerates all input devices
- Filters by capability (must have side buttons + relative axes)
- Selects the first supported device
- Reports device name to user

**Not responsible for:**
- Reading events
- Window detection
- Event filtering

**Implementation:** `src/mouseflow/discovery.py`

---

### Input Engine

**Responsibility:** Continuously read raw input events and convert them to domain objects.

**Input:** Device path (`str`)

**Output:** `Generator[UserInput]` - yields domain events as they occur

**Key behaviors:**
- Opens device and reads event loop
- Filters supported events (BTN_SIDE, BTN_EXTRA, BTN_FORWARD, REL_HWHEEL)
- Converts evdev events to internal MouseEvent/Gesture objects
- Converts internal objects to UserInput for pipeline consumption
- Maps REL_HWHEEL events to THUMB_WHEEL_LEFT/THUMB_WHEEL_RIGHT identifiers
- Yields UserInput objects lazily via generator
- Handles device disconnection gracefully

**Not responsible for:**
- Event routing or interpretation
- Action execution
- Window detection
- Displaying events

**Implementation:** `src/mouseflow/engine.py`

---

### Gesture Recognizer

**Responsibility:** Recognize directional mouse gestures performed while holding a gesture button.

**Input:**
- `MouseEvent` objects from Input Engine (button press/release)
- Movement deltas (REL_X, REL_Y) from Input Engine

**Output:** `Gesture | None` - recognized gesture or None if no gesture

**Key behaviors:**
- Activates gesture mode when gesture button (BTN_EXTRA) is pressed
- Tracks cumulative mouse movement while gesture mode is active
- Recognizes directional gestures (UP, DOWN, LEFT, RIGHT) based on movement thresholds
- Produces Gesture domain object when gesture button is released with sufficient movement
- Resets state when gesture button is released
- Uses threshold-based algorithm (50 pixels) to prevent accidental triggers

**Not responsible for:**
- Loading configuration
- Executing actions
- Window resolution
- Event dispatching

**Implementation:** `src/mouseflow/gesture.py`

---

### Window Resolver

**Responsibility:** Identify the currently focused window and extract application/title information.

**Input:** None (queries compositor on demand)

**Output:** `WindowInfo | None` - current window context or None if unavailable

**Key behaviors:**
- Connects to Sway IPC (via `i3ipc` library)
- Queries focused window tree
- Extracts `app_id` (or `window_class` fallback) and `name`
- Converts to `Application` and `Window` domain objects
- Returns `WindowInfo` aggregating both
- Handles IPC failures gracefully (returns None)

**Not responsible for:**
- Mouse event processing
- Event routing
- Action execution
- Caching window state

**Implementation:** `src/mouseflow/resolver.py`

---

### Event Dispatcher

**Responsibility:** Orchestrate the combination of user inputs with window information.

**Input:** 
- `Iterable[UserInput]` from Input Engine
- `WindowResolver` instance (dependency injection)

**Output:** `Generator[DispatchContext]` - yields unified context for each input

**Key behaviors:**
- Receives UserInput objects from Input Engine
- For each input, calls `resolver.resolve()` to get current window
- Combines `UserInput` + `WindowInfo` into `DispatchContext`
- Handles window resolution failures (passes None)
- Processes inputs independently (no state)
- Depends only on domain abstractions (WindowResolver protocol)

**Not responsible for:**
- Loading configuration
- Executing actions
- Hardware interaction
- Infrastructure details (evdev, i3ipc)

**Implementation:** `src/mouseflow/dispatcher.py`

---

### Domain Model

**Responsibility:** Represent core business concepts as immutable objects.

**Key objects:**
- `UserInput` - unified representation of any user interaction (button, gesture, wheel)
- `InputIdentifier` - enum of all possible input identifiers (BTN_SIDE, GESTURE_UP, etc.)
- `MouseEvent` - internal representation of mouse button/wheel events (used by Input Engine)
- `Gesture` - internal representation of directional gestures (used by GestureRecognizer)
- `GestureDirection` - enum of gesture directions (UP, DOWN, LEFT, RIGHT)
- `Application` - active application name
- `Window` - window title
- `WindowInfo` - aggregates Application + Window
- `DispatchContext` - combines UserInput + WindowInfo
- `Action` - executable action (keyboard shortcut or command)
- `Profile` - application-specific action mappings
- `Configuration` - collection of profiles loaded at startup

**Key behaviors:**
- All objects are frozen dataclasses (immutable)
- Value-based equality (automatic via dataclass)
- Type-safe via enums and type hints
- No infrastructure dependencies
- UserInput is the public API for the pipeline; MouseEvent and Gesture are internal to Input Engine

**Not responsible for:**
- Reading hardware events
- Communicating with compositor
- Executing actions
- Parsing configuration files

**Implementation:** `src/mouseflow/domain.py`

---

### Service Layer

**Responsibility:** Expose application capabilities as a public API for external interfaces (CLI, future GUI).

**Input:** Service method calls from CLI (via IPC) or other interfaces

**Output:** Domain objects or operational result objects

**Key behaviors:**
- Wraps existing components with a clean, high-level API
- Provides operational commands (list devices, reload config, get status)
- Used by CLI via IPC and potentially by future interfaces
- Returns domain objects (Configuration) or operational result objects (DeviceInfo, ApplicationStatus)
- Handles errors and returns structured results
- Combines multiple components for complex operations

**Not responsible for:**
- Parsing command-line arguments
- IPC communication
- Infrastructure details
- Business logic (delegates to components)
- Processing input events

**Implementation:** `src/mouseflow/services.py`

---

### Configuration Parser

**Responsibility:** Parse configuration files and translate them into domain objects.

**Input:** Configuration file path (e.g., `~/.config/mouseflow/config.yaml`)

**Output:** `Configuration` domain object containing `Profile` objects with action mappings

**Key behaviors:**
- Reads YAML configuration file
- Validates structure and required fields
- Translates external format into domain objects (Configuration, Profile, Action)
- Reports clear validation errors for invalid configuration

**Not responsible for:**
- Action resolution
- Event processing
- Action execution
- Runtime configuration changes

**Implementation:** `src/mouseflow/parser.py`

---

### Configuration Loader

**Responsibility:** Resolve which action, if any, matches a dispatched input context using a selected profile.

**Input:**
- `DispatchContext` from Event Dispatcher
- `Profile | None` from Profile Resolver

**Output:** `Action | None` - the resolved action, or None if no match

**Key behaviors:**
- Receives DispatchContext containing UserInput information
- Receives selected Profile from Profile Resolver
- Finds the mapping for the specific InputIdentifier in the profile
- Returns the corresponding Action, or None if no match

**Not responsible for:**
- Parsing configuration files
- Input processing
- Profile selection
- Action execution
- Hardware interaction

**Implementation:** `src/mouseflow/loader.py`

---

### Profile Resolver

**Responsibility:** Select the appropriate profile (application-specific or global) based on the focused application.

**Input:**
- `Configuration` from startup
- `WindowInfo | None` from Event Dispatcher

**Output:** `Profile | None` - the selected profile, or None if no profile available

**Key behaviors:**
- Receives Configuration containing all profiles
- Receives WindowInfo containing the active application
- Looks up the application-specific profile first
- Falls back to global profile if no application-specific profile exists
- Returns None if neither profile is available
- Applies deterministic precedence rules (application-specific always wins)

**Not responsible for:**
- Parsing configuration files
- Event processing
- Action resolution
- Action execution
- Hardware interaction

**Implementation:** `src/mouseflow/profile_resolver.py`

---

### Action Runner

**Responsibility:** Execute actions using a ports and adapters pattern.

**Input:** `Action` domain object

**Output:** `ExecutionResult` domain object

**Key behaviors:**
- Orchestrates action execution through specialized adapters
- Dispatches to appropriate adapter based on action type
- Handles unknown action types gracefully
- Returns execution results with status and error information

**Architecture:**
The Action Runner uses a **ports and adapters** (hexagonal) pattern:

```
Action
  │
  ▼
Action Runner (Orchestrator)
  │
  ├──▶ KeyboardAdapter (Port: ActionExecutor)
  │         │
  │         ▼
  │    pynput (Infrastructure)
  │
  └──▶ ShellAdapter (Port: ActionExecutor)
            │
            ▼
       subprocess (Infrastructure)
```

- **Port:** `ActionExecutor` protocol defines the contract for action execution
- **Adapters:** `KeyboardAdapter` and `ShellAdapter` implement the protocol
- **Orchestrator:** `ActionRunner` dispatches to the appropriate adapter

**Not responsible for:**
- Event routing
- Configuration loading
- Hardware interaction (delegated to adapters)

**Implementation:** `src/mouseflow/runner.py`

---

### Daemon

**Responsibility:** Manage the application lifecycle (startup, shutdown, signal handling) and expose operational interface.

**Input:** None (orchestrates other components)

**Output:** None (manages process lifecycle)

**Key behaviors:**
- Configures logging infrastructure at startup
- Initializes all components in correct order (device discovery, configuration, resolver, dispatcher, profile resolver)
- Registers signal handlers for SIGTERM and SIGINT
- Runs the event processing loop
- Coordinates graceful shutdown on signal or error
- Ensures resources are released via try/finally blocks
- Handles device disconnection and compositor connection loss
- Starts IPC server in a separate thread for CLI communication
- Creates and holds ApplicationServices instance for operational commands
- Supports runtime configuration reload

**Not responsible for:**
- Processing input events
- Resolving or executing actions
- Loading configuration
- Window resolution
- Parsing CLI commands (delegated to CLI component)

**Implementation:** `src/mouseflow/daemon.py`

---

### IPC (Inter-Process Communication)

**Responsibility:** Enable communication between CLI and daemon processes.

**Input:** Command requests from CLI (JSON over Unix socket)

**Output:** Command responses to CLI (JSON over Unix socket)

**Key behaviors:**
- Daemon starts Unix socket server in a separate thread at startup
- CLI connects to socket and sends JSON command requests
- Server dispatches requests to appropriate service methods
- Returns JSON responses to CLI
- Handles connection errors gracefully
- Manages socket file lifecycle (creation, cleanup)
- Supports concurrent CLI invocations

**Protocol:**
- Request format: `{"command": "...", "args": {...}}`
- Response format: `{"status": "ok"|"error", "data": {...}}`

**Socket location:** `~/.local/state/mouseflow/mouseflow.sock`

**Not responsible for:**
- Command parsing (delegated to CLI)
- Business logic (delegated to Service Layer)
- Service implementation

**Implementation:** `src/mouseflow/ipc.py`

---

### CLI

**Responsibility:** Parse user commands and invoke application services via IPC.

**Input:** Command-line arguments

**Output:** Human-readable results (stdout)

**Key behaviors:**
- Parses command-line arguments using argparse
- Validates command and arguments
- Connects to running daemon via Unix socket
- Sends command request and receives JSON response
- Formats and displays results to user
- Exits after completing command
- Provides clear error messages when daemon is not running

**Commands:**
- `start` - Start MouseFlow daemon
- `status` - Show application status
- `devices` - List available devices
- `config show` - Show loaded configuration
- `config validate` - Validate configuration file
- `config reload` - Reload configuration

**Not responsible for:**
- Implementing business logic
- Processing input events
- Managing application lifecycle (delegates to daemon via `start` command)
- Direct infrastructure interaction (delegates to services via IPC)

**Implementation:** `src/mouseflow/cli.py`

---

## Domain Objects

The domain model is the **public API** of MouseFlow. Components communicate exclusively through domain objects.

### Core Objects

```python
@dataclass(frozen=True)
class UserInput:
    identifier: InputIdentifier

class InputIdentifier(Enum):
    # Buttons
    BTN_SIDE = "BTN_SIDE"
    BTN_EXTRA = "BTN_EXTRA"
    BTN_FORWARD = "BTN_FORWARD"
    BTN_BACK = "BTN_BACK"
    # Gestures
    GESTURE_UP = "GESTURE_UP"
    GESTURE_DOWN = "GESTURE_DOWN"
    GESTURE_LEFT = "GESTURE_LEFT"
    GESTURE_RIGHT = "GESTURE_RIGHT"
    # Thumb Wheel
    THUMB_WHEEL_LEFT = "THUMB_WHEEL_LEFT"
    THUMB_WHEEL_RIGHT = "THUMB_WHEEL_RIGHT"

@dataclass(frozen=True)
class Application:
    app_name: str  # "Unknown" if unavailable

@dataclass(frozen=True)
class Window:
    title: str  # "Untitled" if unavailable

@dataclass(frozen=True)
class WindowInfo:
    application: Application
    window: Window

@dataclass(frozen=True)
class DispatchContext:
    event: UserInput  # Unified input type
    window_info: WindowInfo | None  # None if resolution failed

@dataclass(frozen=True)
class Action:
    action_type: ActionType  # KEYBOARD or COMMAND
    payload: str  # "alt+left" or "swaymsg workspace 1"

@dataclass(frozen=True)
class Profile:
    app_name: str
    mappings: dict[InputIdentifier, Action]  # Unified mapping

@dataclass(frozen=True)
class Configuration:
    profiles: tuple[Profile, ...]  # Immutable collection of profiles

@dataclass(frozen=True)
class ExecutionResult:
    action: Action
    status: ExecutionStatus  # SUCCESS or FAILURE
    error_message: str | None = None

class ActionExecutor(Protocol):
    def execute(self, action: Action) -> ExecutionResult: ...
```

### Internal Objects (Input Engine)

These objects are used internally by the Input Engine and GestureRecognizer, then converted to `UserInput` before entering the pipeline:

```python
@dataclass(frozen=True)
class MouseEvent:
    event_type: EventType  # BUTTON or WHEEL
    button: MouseButton | None
    wheel: WheelAxis | None
    value: int

@dataclass(frozen=True)
class Gesture:
    direction: GestureDirection
```

### Operational Objects (Service Layer)

These objects are used by the Service Layer and CLI for operational commands. They represent operational results, not core domain concepts:

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
```

### Design Principles

- **Immutability**: All objects are frozen dataclasses
- **Value equality**: Objects with same values are equal
- **Explicit modeling**: No primitive obsession
- **Infrastructure independence**: Domain never knows about evdev/i3ipc
- **Unified pipeline**: UserInput is the single type that flows through the pipeline

---

## Data Flow Example

### Startup Phase

1. **Configuration Parser** reads `~/.config/mouseflow/config.yaml`
2. **Configuration Parser** validates structure and required fields
3. **Configuration Parser** translates YAML into `Configuration` domain object
4. Application stores `Configuration` for use during input processing

### Input Processing Phase

When the user presses BTN_SIDE in Firefox:

1. **Input Engine** reads evdev event → converts to internal `MouseEvent`
2. **Input Engine** converts `MouseEvent` to `UserInput(identifier=BTN_SIDE)`
3. **Event Dispatcher** receives UserInput
4. **Event Dispatcher** calls `resolver.resolve()` → gets `WindowInfo(app="firefox", title="ChatGPT")`
5. **Event Dispatcher** yields `DispatchContext(event=..., window_info=...)`
6. **Configuration Loader** looks up Profile for "firefox" in Configuration → finds mapping for BTN_SIDE
7. **Action Runner** dispatches to `KeyboardAdapter` → executes `Action(type=KEYBOARD, payload="alt+left")`
8. **Action Runner** returns `ExecutionResult(action=..., status=SUCCESS)`

Each step receives domain objects and produces domain objects. Infrastructure is confined to the edges.

### CLI Command Flow

When the user executes a CLI command (e.g., `mouseflow devices`):

1. **CLI** parses command-line arguments → identifies `devices` command
2. **CLI** connects to daemon via Unix socket (`~/.local/state/mouseflow/mouseflow.sock`)
3. **CLI** sends JSON request: `{"command": "devices", "args": {}}`
4. **IPC Server** (daemon thread) receives request
5. **IPC Server** dispatches to `ApplicationServices.list_devices()`
6. **Service Layer** calls `DeviceDiscovery.find_all_supported_devices()`
7. **Service Layer** converts results to `DeviceInfo` objects
8. **IPC Server** serializes response to JSON: `{"status": "ok", "data": [...]}`
9. **CLI** receives JSON response
10. **CLI** formats and displays results to user
11. **CLI** exits

The CLI operates independently of the event processing pipeline. It queries the daemon's runtime state via IPC without interfering with mouse event processing.

### Key Insight: Unified Input Pipeline

All types of user input (buttons, gestures, thumb wheel) flow through the same pipeline as `UserInput` objects. The Configuration Loader uses `InputIdentifier` as the mapping key, eliminating the need for separate mapping dictionaries or type-specific branching logic.

---

## Architectural Principles

### 1. Pipeline Transformation

The application is a pipeline where each stage transforms domain objects. Components do not "jump" stages or depend on implementations they don't directly consume.

### 2. Dependency Inversion

High-level components (Event Dispatcher) depend on abstractions (WindowResolver protocol), not low-level implementations (SwayResolver). This enables:
- Easy testing with mocks
- Future compositor support without changing dispatcher
- Clear component boundaries

### 3. Single Responsibility

Each component has one job:
- Input Engine: convert events
- Window Resolver: resolve windows
- Event Dispatcher: combine context
- Configuration Parser: parse configuration files into domain objects
- Configuration Loader: resolve actions from configuration
- Action Runner: execute actions
- Service Layer: expose application capabilities as public API
- IPC: enable CLI-daemon communication
- CLI: parse commands and invoke services

### 4. Domain Purity

The domain model has zero infrastructure dependencies. It can be tested, understood, and evolved independently.

### 5. Generator-Based Flow

Event processing uses Python generators for:
- Lazy evaluation (events processed on demand)
- Memory efficiency (no buffering)
- Natural composition (`dispatcher.dispatch(read_events(path))`)
- Easy testing (mock generators)

---

## Dependencies

```
mouseflow/
├── domain.py          # No dependencies (pure domain)
├── discovery.py       # Depends on: evdev
├── engine.py          # Depends on: evdev, domain, logging
├── resolver.py        # Depends on: i3ipc, domain, logging
├── dispatcher.py      # Depends on: domain, resolver (protocol)
├── parser.py          # Depends on: yaml, domain
├── loader.py          # Depends on: domain
├── runner.py          # Depends on: domain, pynput, subprocess
├── services.py        # Depends on: domain, discovery, parser, daemon (state)
├── ipc.py             # Depends on: socket, json, services
├── cli.py             # Depends on: argparse, ipc, domain
└── daemon.py          # Depends on: discovery, engine, dispatcher, parser,
                       #            resolver, loader, runner, services, ipc,
                       #            signal, logging
```

**Key observations:**
- `domain.py` has no dependencies (pure Python)
- Infrastructure libraries (evdev, i3ipc, yaml, pynput) are confined to specific modules
- `dispatcher.py` depends on resolver protocol, not implementation
- `parser.py` is the only module that knows about YAML
- `loader.py` depends only on domain objects, not on file formats
- `runner.py` uses ports and adapters pattern: ActionRunner depends on ActionExecutor protocol, not concrete adapters
- `services.py` wraps components and exposes application capabilities as a public API
- `ipc.py` uses stdlib `socket` and `json` for CLI-daemon communication
- `cli.py` uses stdlib `argparse` for command parsing, no external dependencies
- `daemon.py` orchestrates the application lifecycle and depends on all major components including services and IPC
- `logging` module (stdlib) is used across modules for structured logging
- No circular dependencies

---

## Ports and Adapters Pattern

The Action Runner implements the **ports and adapters** (hexagonal) architecture pattern to separate orchestration from infrastructure concerns.

### Pattern Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Domain Layer                          │
│  ┌─────────────┐                                       │
│  │   Action    │                                       │
│  └──────┬──────┘                                       │
│         │                                               │
│         ▼                                               │
│  ┌─────────────────┐                                   │
│  │  ActionExecutor │ ← Port (Protocol)                 │
│  │    (Protocol)   │                                   │
│  └────────┬────────┘                                   │
│           │                                             │
└───────────┼─────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│               Application Layer                          │
│  ┌─────────────────┐                                   │
│  │  ActionRunner   │ ← Orchestrator                    │
│  │                 │                                   │
│  │  - Dispatches   │                                   │
│  │  - Delegates    │                                   │
│  └────────┬────────┘                                   │
│           │                                             │
└───────────┼─────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│               Infrastructure Layer                       │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │ KeyboardAdapter │    │  ShellAdapter   │            │
│  │                 │    │                 │            │
│  │  - pynput       │    │  - subprocess   │            │
│  │  - key mapping  │    │  - timeout      │            │
│  └─────────────────┘    └─────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Benefits

1. **Separation of Concerns:** Orchestrator (ActionRunner) doesn't know about infrastructure details
2. **Testability:** Adapters can be mocked independently
3. **Extensibility:** New action types (mouse gestures, window management) can be added as new adapters
4. **Consistency:** Follows the same pattern as WindowResolver (protocol-based dependency inversion)

### Adding New Action Types

To add a new action type:

1. Define the action type in `ActionType` enum (domain.py)
2. Create a new adapter implementing `ActionExecutor` protocol
3. Register the adapter in `ActionRunner.create_default()`

Example:
```python
# New adapter
class MouseAdapter:
    def execute(self, action: Action) -> ExecutionResult:
        # Mouse-specific execution logic
        ...

# Register in ActionRunner
executors = {
    ActionType.KEYBOARD: KeyboardAdapter.create_default(),
    ActionType.COMMAND: ShellAdapter(),
    ActionType.MOUSE: MouseAdapter(),  # New adapter
}
```

---

## Testing Strategy

Each component is tested in isolation:

- **Domain objects**: Test creation, equality, immutability
- **Input Engine**: Mock evdev, test event conversion
- **Window Resolver**: Mock i3ipc, test window resolution
- **Event Dispatcher**: Mock WindowResolver, test context creation
- **Configuration Parser**: Test YAML parsing, validation, and translation
- **Configuration Loader**: Test action resolution with mock Configuration
- **Action Runner**: Test orchestration with mock adapters
- **Keyboard Adapter**: Mock pynput, test key execution
- **Shell Adapter**: Mock subprocess, test command execution
- **Service Layer**: Mock components, test service methods and result objects
- **IPC**: Mock socket communication, test request/response handling
- **CLI**: Mock IPC client, test command parsing and output formatting
- **Integration tests**: Test full pipeline with mocked infrastructure

This ensures tests are fast, deterministic, and focused.

---

## Future Evolution

The pipeline architecture supports future extensions:

- **Multiple Configuration Formats**: Add parsers for TOML, JSON without changing Loader
- **Gesture Recognition**: Add as new stage between Engine and Dispatcher
- **Multiple Profiles**: Extend Configuration to merge profiles from multiple sources
- **Plugin System**: Add plugin stage before Action Runner
- **Remote Configuration**: Add API-based configuration source alongside file-based
- **GUI Interface**: Add graphical interface using same Service Layer API

Each extension is a new pipeline stage or enhancement to existing stage, without disrupting the overall architecture.
