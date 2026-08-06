# ADR-006: Keep Manual Serialization for IPC Protocol

## Status

Accepted

## Context

The IPC module needs to serialize domain objects to JSON for transmission between CLI and daemon processes. The initial implementation uses manual serialization functions with `dataclasses.asdict()` for simple cases and custom logic for complex cases.

Current serialization approach:
- `_serialize_device_info()`: Uses `asdict()` directly for simple dataclass
- `_serialize_configuration()`: Custom logic to handle nested structures and enums
- `_serialize_result()`: Generic function using `asdict()` for any dataclass

The `Configuration` object requires special handling because:
- `Profile.mappings` is a dict with `InputIdentifier` enum keys
- `Action.action_type` is an enum that needs string conversion
- Nested structures need proper JSON-compatible representation

## Decision

Keep the current manual serialization approach rather than implementing a generic serializer framework.

## Alternatives Considered

### 1. Generic Serializer Framework

Create a reusable serializer that handles enums, nested dataclasses, and custom types automatically.

**Pros:**
- Reusable across the project
- Less code duplication
- Easier to add new serializable types

**Cons:**
- Over-engineering for current needs
- Adds complexity with reflection/magic
- Harder to debug serialization issues
- Only 3 types need serialization currently

**Why not chosen:** The project has only 3 serializable types. A generic framework would add complexity without clear benefit. The manual approach is explicit and easy to understand.

### 2. Use `dataclasses.asdict()` Everywhere

Rely solely on `asdict()` for all serialization.

**Pros:**
- Simple, built-in solution
- Less code to maintain

**Cons:**
- Doesn't handle enums properly (serializes as enum objects, not strings)
- Doesn't handle dict keys that are enums
- Would produce invalid JSON for Configuration

**Why not chosen:** `asdict()` doesn't handle enums correctly for JSON serialization. Enums need to be converted to their string values.

### 3. Use External Serialization Library

Use libraries like `pydantic`, `marshmallow`, or `attrs` for serialization.

**Pros:**
- Robust, well-tested solutions
- Handle complex cases automatically
- Validation support

**Cons:**
- Adds external dependencies (violates "prefer standard library")
- Overkill for simple IPC protocol
- Learning curve for contributors

**Why not chosen:** The project prefers standard library over external dependencies. The serialization needs are simple enough that stdlib is sufficient.

### 4. Keep Current Manual Approach (Chosen)

Maintain explicit serialization functions with custom logic where needed.

**Pros:**
- Explicit and easy to understand
- No external dependencies
- Easy to debug
- Handles all edge cases correctly
- Follows "simplest solution that works" principle

**Cons:**
- Need to write serialization code for each new type
- Some code duplication

**Why chosen:** The current approach is simple, explicit, and works correctly. The project has only 3 serializable types, so the maintenance burden is minimal. If more types need serialization in the future, we can reassess.

## Trade-offs

### Pros

1. **Simplicity:** No complex serialization framework to understand
2. **Explicit:** Each serialization function is clear about what it does
3. **No dependencies:** Uses only stdlib (`dataclasses.asdict`, `json`)
4. **Easy to debug:** Serialization logic is visible and straightforward
5. **Correct handling:** Properly handles enums and nested structures

### Cons

1. **Manual work:** Need to write serialization code for each type
2. **Potential duplication:** Similar patterns across serialization functions
3. **Maintenance:** If domain objects change, serialization functions need updates

## Consequences

### Positive

- IPC serialization is simple and maintainable
- No external dependencies added
- Easy to understand for new contributors
- Correct JSON output for all domain objects

### Negative

- Adding new serializable types requires writing serialization code
- Need to remember to update serialization when domain objects change

### Neutral

- Current approach is sufficient for project needs
- Can be refactored later if serialization needs grow significantly

## Implementation

Current serialization functions in `src/mouseflow/ipc.py`:

```python
def _serialize_device_info(devices: list[DeviceInfo]) -> list[dict[str, Any]]:
    return [asdict(d) for d in devices]

def _serialize_configuration(config: Configuration | None) -> dict[str, Any] | None:
    if config is None:
        return None
    profiles = []
    for profile in config.profiles:
        mappings = {}
        for input_id, action in profile.mappings.items():
            mappings[input_id.value] = {
                "type": action.action_type.value.lower(),
                "payload": action.payload,
            }
        profiles.append({
            "app_name": profile.app_name,
            "mappings": mappings,
        })
    return {"profiles": profiles}

def _serialize_result(result: Any) -> dict[str, Any]:
    if hasattr(result, "__dataclass_fields__"):
        return asdict(result)
    return {}
```

## Related Decisions

- **ADR-003:** Unix socket for IPC (defines the communication mechanism)
- **Project principles:** "Prefer the standard library unless there is a compelling reason not to"

## References

- [dataclasses.asdict() documentation](https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict)
- [JSON encoding/decoding](https://docs.python.org/3/library/json.html)
- Project AGENTS.md: "Prefer the standard library unless there is a compelling reason not to"
