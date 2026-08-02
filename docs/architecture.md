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
│  Input Engine   │ ← Converts raw events to MouseEvent
└────────┬────────┘
         │ MouseEvent
         ▼
┌─────────────────┐
│    Window       │ ← Resolves focused window
│   Resolver      │
└────────┬────────┘
         │ WindowInfo
         ▼
┌─────────────────┐
│     Event       │ ← Combines event + window context
│   Dispatcher    │
└────────┬────────┘
         │ DispatchContext
         ▼
┌─────────────────┐
│  Config Loader  │ ← Loads user mappings (future)
└────────┬────────┘
         │ Profile + Action
         ▼
┌─────────────────┐
│  Action Runner  │ ← Executes actions (future)
└─────────────────┘
```

Each arrow represents a domain object being passed from one component to the next. Infrastructure details (evdev, i3ipc, file I/O) are confined to the edges and never leak into the domain.

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

**Output:** `Generator[MouseEvent]` - yields domain events as they occur

**Key behaviors:**
- Opens device and reads event loop
- Filters supported events (BTN_SIDE, BTN_EXTRA, BTN_FORWARD, REL_HWHEEL)
- Converts evdev events to `MouseEvent` domain objects
- Yields events lazily via generator
- Handles device disconnection gracefully

**Not responsible for:**
- Event routing or interpretation
- Action execution
- Window detection
- Displaying events

**Implementation:** `src/mouseflow/engine.py`

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

**Responsibility:** Orchestrate the combination of mouse events with window information.

**Input:** 
- `Iterable[MouseEvent]` from Input Engine
- `WindowResolver` instance (dependency injection)

**Output:** `Generator[DispatchContext]` - yields unified context for each event

**Key behaviors:**
- Receives mouse events from Input Engine
- For each event, calls `resolver.resolve()` to get current window
- Combines `MouseEvent` + `WindowInfo` into `DispatchContext`
- Handles window resolution failures (passes None)
- Processes events independently (no state)
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
- `MouseEvent` - mouse button press or wheel scroll
- `Application` - active application name
- `Window` - window title
- `WindowInfo` - aggregates Application + Window
- `DispatchContext` - combines MouseEvent + WindowInfo
- `Action` - executable action (keyboard shortcut or command)
- `Profile` - application-specific action mappings

**Key behaviors:**
- All objects are frozen dataclasses (immutable)
- Value-based equality (automatic via dataclass)
- Type-safe via enums and type hints
- No infrastructure dependencies

**Not responsible for:**
- Reading hardware events
- Communicating with compositor
- Executing actions
- Loading configuration

**Implementation:** `src/mouseflow/domain.py`

---

### Configuration Loader (Future)

**Responsibility:** Load user-defined action mappings from YAML files.

**Input:** Configuration file path

**Output:** `Profile` objects with action mappings

**Key behaviors:**
- Reads YAML configuration
- Validates structure
- Converts to domain objects (Profile, Action)
- Handles missing/invalid files gracefully

**Not responsible for:**
- Event processing
- Action execution
- Hardware interaction

**Implementation:** Not yet implemented (Sprint 6)

---

### Action Runner (Future)

**Responsibility:** Execute actions (keyboard shortcuts, shell commands).

**Input:** `Action` domain object

**Output:** Side effects (key presses, command execution)

**Key behaviors:**
- Interprets action type (keyboard vs command)
- Executes appropriate system call
- Handles execution failures

**Not responsible for:**
- Event routing
- Configuration loading
- Hardware interaction

**Implementation:** Not yet implemented (Sprint 7)

---

## Domain Objects

The domain model is the **public API** of MouseFlow. Components communicate exclusively through domain objects.

### Core Objects

```python
@dataclass(frozen=True)
class MouseEvent:
    event_type: EventType  # BUTTON or WHEEL
    button: MouseButton | None
    wheel: WheelAxis | None
    value: int

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
    event: MouseEvent
    window_info: WindowInfo | None  # None if resolution failed

@dataclass(frozen=True)
class Action:
    action_type: ActionType  # KEYBOARD or COMMAND
    payload: str  # "alt+left" or "swaymsg workspace 1"

@dataclass(frozen=True)
class Profile:
    app_name: str
    mappings: dict[str, Action]  # "BTN_SIDE" -> Action
```

### Design Principles

- **Immutability**: All objects are frozen dataclasses
- **Value equality**: Objects with same values are equal
- **Explicit modeling**: No primitive obsession
- **Infrastructure independence**: Domain never knows about evdev/i3ipc

---

## Data Flow Example

When the user presses BTN_SIDE in Firefox:

1. **Input Engine** reads evdev event → converts to `MouseEvent(button=BTN_SIDE, value=1)`
2. **Event Dispatcher** receives MouseEvent
3. **Event Dispatcher** calls `resolver.resolve()` → gets `WindowInfo(app="firefox", title="ChatGPT")`
4. **Event Dispatcher** yields `DispatchContext(event=..., window_info=...)`
5. **Config Loader** (future) looks up Profile for "firefox" → finds mapping for BTN_SIDE
6. **Action Runner** (future) executes `Action(type=KEYBOARD, payload="alt+left")`

Each step receives domain objects and produces domain objects. Infrastructure is confined to the edges.

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
- Config Loader: load mappings
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
└── dispatcher.py      # Depends on: domain, resolver (protocol)
```

**Key observations:**
- `domain.py` has no dependencies (pure Python)
- Infrastructure libraries (evdev, i3ipc) are confined to specific modules
- `dispatcher.py` depends on resolver protocol, not implementation
- No circular dependencies

---

## Testing Strategy

Each component is tested in isolation:

- **Domain objects**: Test creation, equality, immutability
- **Input Engine**: Mock evdev, test event conversion
- **Window Resolver**: Mock i3ipc, test window resolution
- **Event Dispatcher**: Mock WindowResolver, test context creation
- **Integration tests**: Test full pipeline with mocked infrastructure

This ensures tests are fast, deterministic, and focused.

---

## Future Evolution

The pipeline architecture supports future extensions:

- **Config Loader** (Sprint 6): Add between Dispatcher and Action Runner
- **Action Runner** (Sprint 7): Add at end of pipeline
- **Gesture Recognition**: Add as new stage between Engine and Dispatcher
- **Multiple Profiles**: Extend Config Loader to merge profiles
- **Plugin System**: Add plugin stage before Action Runner

Each extension is a new pipeline stage or enhancement to existing stage, without disrupting the overall architecture.
