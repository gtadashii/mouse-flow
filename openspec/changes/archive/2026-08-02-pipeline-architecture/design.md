## Context

See proposal.md for motivation. The project currently has independent components (Input Engine, Window Resolver) that operate without a clear transformation pipeline. This design establishes the architectural foundation for a pipeline where each component transforms domain objects for the next stage, preparing for the Event Dispatcher (Sprint 5).

## Goals / Non-Goals

**Goals:**
- Establish a clear pipeline architecture with defined input/output contracts
- Move WindowInfo into the domain model as a first-class object
- Refactor Input Engine to separate event production from presentation
- Add DispatchContext as the unified output for orchestration
- Enable testability of each pipeline stage in isolation

**Non-Goals:**
- Implement the Event Dispatcher (Sprint 5)
- Implement configuration loading (Sprint 6)
- Implement action execution (Sprint 7)
- Change the external behavior of the application (user-facing output remains the same)

## Decisions

### Decision 1: Generator-based API for Input Engine

**Choice:** Expose `read_events(device_path) -> Generator[MouseEvent]` that yields domain events.

**Rationale:**
- Separates event production from consumption
- Enables lazy evaluation and memory efficiency
- Allows multiple consumers (dispatcher, logger, etc.)
- Natural fit for continuous event streams
- Easy to test with mock generators

**Alternatives considered:**
- Callback-based API: More complex, harder to compose
- Queue-based API: Overkill for single-producer scenario
- Keep run_engine() with callback parameter: Still mixes concerns

### Decision 2: WindowInfo as domain object

**Choice:** Move WindowInfo from resolver.py to domain.py, keeping it as a frozen dataclass that aggregates Application + Window.

**Rationale:**
- WindowInfo is used by multiple components (resolver, dispatcher, future config loader)
- Belongs in the domain as it represents a business concept
- Keeps Application and Window as separate objects for flexibility
- Maintains immutability and value-based equality

**Alternatives considered:**
- Keep WindowInfo in resolver.py: Breaks domain purity, harder to share
- Flatten to (app_name, title) tuple: Loses type safety and structure
- Make WindowInfo inherit from Application/Window: Unnecessary complexity

### Decision 3: DispatchContext composition

**Choice:** DispatchContext is a frozen dataclass containing MouseEvent + WindowInfo (optional).

**Rationale:**
- Represents the unified context for orchestration
- WindowInfo is optional to handle resolution failures gracefully
- Immutable and testable
- Clear input for Config Loader (Sprint 6)

**Alternatives considered:**
- Flatten fields (event_type, button, app_name, title): Loses structure, harder to evolve
- Use dict or loose structure: No type safety, error-prone
- Inherit from MouseEvent: Confusing, WindowInfo is not a mouse event

### Decision 4: Pipeline stage contracts

**Choice:** Each stage has explicit input/output types:
- Input Engine: `str -> Generator[MouseEvent]`
- Window Resolver: `() -> WindowInfo | None`
- Event Dispatcher: `MouseEvent + WindowResolver -> DispatchContext`

**Rationale:**
- Clear contracts enable independent testing
- Type hints provide IDE support and static analysis
- Easy to add new stages without modifying existing ones
- Follows composition over inheritance

**Alternatives considered:**
- Implicit contracts (duck typing): Harder to understand and test
- Shared mutable state: Breaks immutability principle
- Event bus pattern: Overkill for current scope

## Risks / Trade-offs

**[Risk] Breaking existing Input Engine API** → Mitigation: Keep run_engine() as a convenience wrapper that consumes read_events() and prints. Existing tests can be updated to use the new API.

**[Risk] WindowInfo duplication** → Mitigation: Move WindowInfo to domain.py and update resolver.py to import from there. Update tests accordingly.

**[Risk] Generator complexity** → Mitigation: Generators are well-understood Python feature. Provide clear documentation and examples.

**[Trade-off] More domain objects** → The domain model grows (WindowInfo, DispatchContext), but each object has clear responsibility. This is acceptable complexity for the architectural clarity gained.
