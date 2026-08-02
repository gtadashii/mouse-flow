# ADR-001: Ports and Adapters Pattern for Action Execution

## Status

Accepted

## Context

The Action Runner component needed to execute different types of actions (keyboard shortcuts, shell commands) on the operating system. The initial implementation mixed orchestration logic with infrastructure details (pynput for keyboard, subprocess for commands), making it difficult to:

- Test action execution in isolation
- Add new action types without modifying existing code
- Mock infrastructure dependencies cleanly

The project already used protocol-based dependency inversion for `WindowResolver`, establishing a pattern for separating abstractions from implementations.

## Decision

Apply the **Ports and Adapters** (Hexagonal) architecture pattern to the Action Runner:

1. **Port:** Define `ActionExecutor` protocol in the domain layer
2. **Adapters:** Create specialized adapters (`KeyboardAdapter`, `ShellAdapter`) that implement the protocol
3. **Orchestrator:** `ActionRunner` dispatches to the appropriate adapter based on action type

```
Action
  │
  ▼
ActionRunner (Orchestrator)
  │
  ├──▶ KeyboardAdapter (ActionExecutor)
  │         │
  │         ▼
  │    pynput
  │
  └──▶ ShellAdapter (ActionExecutor)
            │
            ▼
       subprocess
```

## Alternatives Considered

### 1. Strategy Pattern with Action Handlers

Use a strategy pattern where each action type has its own handler class.

**Pros:**
- Clear separation of execution logic
- Easy to add new action types

**Cons:**
- Similar to ports and adapters but less explicit about infrastructure boundaries
- Doesn't emphasize the infrastructure isolation aspect

**Why not chosen:** Ports and adapters more clearly expresses the intent to isolate infrastructure from domain logic.

### 2. Registry Pattern with Decorators

Use a registry where adapters register themselves via decorators.

**Pros:**
- Automatic discovery of adapters
- Loose coupling

**Cons:**
- Adds complexity with decorator magic
- Harder to understand the flow
- Over-engineering for 2-3 action types

**Why not chosen:** Simplicity. The explicit registration in `ActionRunner.create_default()` is clearer and easier to understand.

### 3. Keep Original Implementation

Keep the original if/elif chain with private functions.

**Pros:**
- Simpler code (fewer classes)
- No architectural overhead

**Cons:**
- Infrastructure knowledge (pynput key mapping) mixed with orchestration
- Harder to test (must mock internal functions)
- Adding new action types requires modifying the runner

**Why not chosen:** The roadmap includes gestures, thumb wheel, and plugins (Phases 9, 10, 14), which will likely need new action types. The ports and adapters pattern makes extension trivial.

## Trade-offs

### Pros

1. **Separation of Concerns:** Orchestrator doesn't know about infrastructure details
2. **Testability:** Adapters can be mocked independently; tests are cleaner
3. **Extensibility:** New action types require only a new adapter and registration
4. **Consistency:** Follows the same pattern as `WindowResolver` (protocol-based)
5. **Clarity:** Makes the "action execution" concept explicit in the domain

### Cons

1. **More Code:** 3 classes (ActionRunner, KeyboardAdapter, ShellAdapter) instead of functions
2. **Indirection:** Slightly more complex flow to understand
3. **Potential Over-Engineering:** For only 2 action types, this might seem excessive

## Consequences

### Positive

- Adding a new action type (e.g., mouse gestures) requires only:
  1. Create new adapter implementing `ActionExecutor`
  2. Register adapter in `ActionRunner.create_default()`
- Tests are cleaner: mock adapters instead of internal functions
- Infrastructure details (pynput key mapping, subprocess configuration) are isolated in adapters
- Consistent with existing architectural patterns in the project

### Negative

- Slightly more code to maintain
- New contributors need to understand the ports and adapters pattern
- May seem like over-engineering if no new action types are added

## Implementation

The pattern is implemented in `src/mouseflow/runner.py`:

```python
# Port (in domain.py)
class ActionExecutor(Protocol):
    def execute(self, action: Action) -> ExecutionResult: ...

# Adapters (in runner.py)
@dataclass(frozen=True)
class KeyboardAdapter:
    controller: KeyboardController
    key_map: dict[str, object]
    
    def execute(self, action: Action) -> ExecutionResult: ...

@dataclass(frozen=True)
class ShellAdapter:
    timeout: int = 10
    
    def execute(self, action: Action) -> ExecutionResult: ...

# Orchestrator (in runner.py)
@dataclass(frozen=True)
class ActionRunner:
    executors: dict[ActionType, ActionExecutor]
    
    def run(self, action: Action) -> ExecutionResult: ...
```

## Related Decisions

- **ADR-002:** (Future) If new action types are added frequently, consider automatic adapter discovery via registry pattern
- **WindowResolver Protocol:** Similar pattern used for window resolution (SwayResolver implements WindowResolver protocol)

## References

- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports and Adapters Pattern](https://java-design-patterns.com/patterns/ports-and-adapters/)
- Project AGENTS.md: "Prefer composition over inheritance" and "Every module should have a single responsibility"
