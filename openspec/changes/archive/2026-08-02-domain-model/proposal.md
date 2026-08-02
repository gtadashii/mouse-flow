## Why

Current components (Input Engine, Window Resolver) operate independently and exchange raw values. As the project grows, passing primitive values between components will increase coupling and make the codebase harder to understand and evolve. A shared domain model provides a common vocabulary and clear boundaries between components.

## What Changes

- Introduce a dedicated domain module with immutable objects representing core concepts
- Define objects for: MouseEvent, Application, Window, Action, and Profile
- Establish the domain model as the public API for inter-component communication
- Refactor existing components to use domain objects instead of raw values

## Capabilities

### New Capabilities
- `domain-model`: Core domain objects representing mouse events, applications, windows, actions, and profiles

### Modified Capabilities
<!-- No existing specs need modification - this is a new capability -->

## Impact

- **Code**: New `src/mouseflow/domain.py` module (or similar)
- **API**: New public domain objects that future components will consume
- **Dependencies**: None (uses Python standard library: dataclasses, typing)
- **Systems**: No external systems affected; internal refactoring of existing components to use domain objects
