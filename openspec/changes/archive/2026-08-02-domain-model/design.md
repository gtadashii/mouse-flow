## Context

See proposal.md for motivation. The project currently has two working components (Input Engine and Window Resolver) that operate independently. This design establishes the domain model that will enable future components to communicate through well-defined objects.

## Goals / Non-Goals

**Goals:**
- Define immutable domain objects using Python dataclasses
- Establish a clean, type-safe API for inter-component communication
- Keep the domain model independent from infrastructure (evdev, i3ipc)
- Provide a foundation for the Event Dispatcher (Sprint 5)

**Non-Goals:**
- Implement event routing or dispatching (Sprint 5)
- Implement configuration loading (Sprint 6)
- Implement action execution (Sprint 7)
- Refactor existing components to use domain objects (can be done incrementally)

## Decisions

### Decision 1: Use frozen dataclasses for domain objects

**Choice:** Python `@dataclass(frozen=True)` for all domain objects.

**Rationale:**
- Built-in immutability via `frozen=True`
- Automatic `__eq__` implementation for value-based equality
- Type hints provide IDE support and static analysis
- No external dependencies required

**Alternatives considered:**
- Named tuples: Less readable, no default values
- Pydantic models: External dependency, overkill for simple value objects
- Custom classes with `__slots__`: More boilerplate, manual equality implementation

### Decision 2: Single domain module vs. multiple modules

**Choice:** Single `src/mouseflow/domain.py` module containing all domain objects.

**Rationale:**
- Domain objects are tightly related and small in number
- Single module is easier to discover and import
- Reduces file proliferation for a small project
- Can be split later if the domain grows significantly

**Alternatives considered:**
- Multiple modules (`domain/events.py`, `domain/actions.py`, etc.): Premature abstraction for current scope
- Package with `__init__.py` exposing objects: Adds complexity without clear benefit now

### Decision 3: Enum for event types vs. string literals

**Choice:** Use `Enum` for mouse event types (button names, wheel axes).

**Rationale:**
- Type safety: Prevents typos in event type names
- IDE autocomplete support
- Exhaustive matching with `match` statements
- Self-documenting code

**Alternatives considered:**
- String literals: Simpler but error-prone
- Integer constants: Less readable, no validation

### Decision 4: Action type discrimination

**Choice:** Use a discriminated union with a `type` field to distinguish action types (keyboard, command).

**Rationale:**
- Clear separation of action types
- Easy to extend with new action types
- Type-safe pattern matching
- Simple to serialize/deserialize later

**Alternatives considered:**
- Inheritance hierarchy: Overkill for two action types, adds complexity
- Single class with optional fields: Confusing, allows invalid combinations

## Risks / Trade-offs

**[Risk] Over-modeling too early** → Mitigation: Keep domain objects minimal, only model what's needed for upcoming sprints. Can extend later.

**[Risk] Refactoring existing components breaks working code** → Mitigation: Refactoring is optional for this sprint. New components will use domain objects; existing ones can migrate incrementally.

**[Risk] Enum evolution** → Mitigation: Enums can be extended without breaking changes. Use string values matching evdev constants for compatibility.
