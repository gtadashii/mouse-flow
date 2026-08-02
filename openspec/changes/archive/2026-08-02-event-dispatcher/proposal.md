## Why

The Input Engine and Window Resolver currently operate independently, producing isolated pieces of information. Future features require a unified context that combines mouse events with the active application. Without this orchestration layer, later components would need to coordinate multiple data sources themselves, increasing coupling and complexity.

## What Changes

- Introduce Event Dispatcher as the first orchestration component
- Event Dispatcher receives MouseEvent from Input Engine
- Event Dispatcher obtains WindowInfo from Window Resolver for each event
- Event Dispatcher produces DispatchContext combining both pieces of information
- Application displays the resulting DispatchContext in human-readable format
- No configuration lookup or action execution (deferred to future sprints)

## Capabilities

### New Capabilities
- `event-dispatcher`: Orchestration component that combines mouse events with window information to produce unified DispatchContext objects

### Modified Capabilities
<!-- No existing specs need modification - this is a new capability -->

## Impact

- **Code**: New `src/mouseflow/dispatcher.py` module
- **API**: Event Dispatcher depends on WindowResolver protocol and produces DispatchContext
- **Dependencies**: None (uses existing domain objects and protocols)
- **Systems**: Integrates Input Engine and Window Resolver through domain objects
- **Breaking changes**: None (additive change)
