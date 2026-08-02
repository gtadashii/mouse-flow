## Context

The project has device discovery (Sprint 1) and input engine (Sprint 2) working. The application can find a supported mouse and stream its events. Now we need to identify which window currently has focus, so that future sprints can associate mouse events with specific applications.

The primary target compositor is Sway (Wayland). The solution should be isolated to allow future compositor support without changing the interface.

## Goals / Non-Goals

**Goals:**
- Determine which window currently has focus
- Extract application name from focused window
- Extract window title from focused window
- Present information in human-readable format
- Handle failures gracefully
- Isolate window resolution logic for future compositor support

**Non-Goals:**
- Combine with mouse events (Sprint 4)
- Event routing or action execution
- Configuration loading
- Caching or performance optimization
- Supporting multiple compositors in this sprint (only Sway)

## Decisions

### Decision 1: Use i3ipc library for Sway IPC

**Choice:** i3ipc-python

**Rationale:** i3ipc is the standard Python library for communicating with i3-compatible compositors (including Sway) via IPC. It provides a clean API for querying workspace and window information. It's well-maintained and widely used in the Sway community.

**Alternatives considered:**
- Direct JSON IPC: More complex, requires manual socket management
- subprocess + swaymsg: Less efficient, requires parsing JSON output
- pywayland: Lower-level, more complex for this use case

### Decision 2: Create a WindowInfo dataclass

**Choice:** Return a frozen dataclass with app_name and title fields

**Rationale:** A dataclass provides type safety, immutability, and clear structure. Using a dataclass instead of a dict or tuple makes the code more maintainable and testable.

**Alternatives considered:**
- Return dict: Less type-safe, harder to document
- Return tuple: Less readable, positional access
- Return NamedTuple: Similar to dataclass but less flexible

### Decision 3: Use Protocol for compositor backend abstraction

**Choice:** Define a WindowResolver protocol

**Rationale:** A Protocol allows different compositor backends (Sway, X11, future Wayland compositors) to implement the same interface without inheritance. This follows the project's preference for composition over inheritance.

**Alternatives considered:**
- Abstract base class: Requires inheritance, less flexible
- No abstraction: Would require refactoring for each new compositor
- Union types: Less extensible

### Decision 4: Separate resolver module from engine

**Choice:** Create src/mouseflow/resolver.py as a standalone module

**Rationale:** Single responsibility principle. The resolver only identifies windows; it doesn't process events or combine with other components. This separation makes testing easier and allows independent evolution.

**Alternatives considered:**
- Add to engine.py: Violates single responsibility
- Add to discovery.py: Different concern (devices vs windows)
- Create generic context module: Over-engineering for current needs

### Decision 5: Query on-demand, not continuously

**Choice:** Resolve window information when requested, not in a loop

**Rationale:** The PRD states this sprint focuses on window identification, not continuous monitoring. Future sprints will integrate with the event stream. Querying on-demand is simpler and sufficient for this sprint.

**Alternatives considered:**
- Continuous monitoring: Unnecessary complexity for this sprint
- Event-driven updates: Requires integration with window manager events (future work)

## Risks / Trade-offs

**Risk:** Sway-specific implementation limits portability
→ **Mitigation:** Use Protocol abstraction to allow future backends without changing the interface

**Risk:** i3ipc adds a dependency
→ **Mitigation:** i3ipc is essential for Sway IPC. No standard library alternative exists. It's a lightweight, pure-Python library.

**Risk:** Window metadata may be incomplete or inconsistent
→ **Mitigation:** Handle missing metadata gracefully with fallback values ("Unknown", "Untitled")

**Trade-off:** Only Sway support in this sprint
→ **Acceptance:** Sway is the primary target. X11 and other compositors can be added in future sprints using the Protocol abstraction.

**Trade-off:** On-demand queries instead of continuous monitoring
→ **Acceptance:** Sufficient for this sprint. Continuous monitoring will be added when integrating with the event stream.
