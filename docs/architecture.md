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
├── engine.py          # Depends on: evdev, domain
├── resolver.py        # Depends on: i3ipc, domain
├── dispatcher.py      # Depends on: domain, resolver (protocol)
├── parser.py          # Depends on: yaml, domain
├── loader.py          # Depends on: domain
└── runner.py          # Depends on: domain, pynput, subprocess
```

**Key observations:**
- `domain.py` has no dependencies (pure Python)
- Infrastructure libraries (evdev, i3ipc, yaml, pynput) are confined to specific modules
- `dispatcher.py` depends on resolver protocol, not implementation
- `parser.py` is the only module that knows about YAML
- `loader.py` depends only on domain objects, not on file formats
- `runner.py` uses ports and adapters pattern: ActionRunner depends on ActionExecutor protocol, not concrete adapters
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
- **Integration tests**: Test full pipeline with mocked infrastructure

This ensures tests are fast, deterministic, and focused.

---

## Future Evolution

The pipeline architecture supports future extensions:

- **Configuration Reload**: Replace Configuration object at runtime
- **Multiple Configuration Formats**: Add parsers for TOML, JSON without changing Loader
- **Gesture Recognition**: Add as new stage between Engine and Dispatcher
- **Multiple Profiles**: Extend Configuration to merge profiles from multiple sources
- **Plugin System**: Add plugin stage before Action Runner
- **Remote Configuration**: Add API-based configuration source alongside file-based

Each extension is a new pipeline stage or enhancement to existing stage, without disrupting the overall architecture.
