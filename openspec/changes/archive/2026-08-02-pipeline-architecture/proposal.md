## Why

Current components operate independently without a clear transformation pipeline. The Input Engine mixes event conversion with presentation (printing), WindowInfo is an intermediate structure outside the domain, and there's no unified context object for orchestration. Before implementing the Event Dispatcher (Sprint 5), the architecture needs to evolve into a clean pipeline where each component transforms domain objects for the next stage.

## What Changes

- Move WindowInfo from resolver.py to domain.py as a first-class domain object
- Refactor Input Engine to expose a generator-based API that yields MouseEvent objects
- Add DispatchContext domain object that combines MouseEvent + WindowInfo
- Establish clear input/output contracts for each pipeline stage
- Separate event production (engine) from event consumption (dispatcher)

## Capabilities

### New Capabilities
- `dispatch-context`: Domain object that combines mouse events with window information for orchestration

### Modified Capabilities
- `domain-model`: Add WindowInfo to the domain model as a first-class object (currently in resolver.py)
- `input-engine`: Refactor to expose generator-based event stream API (separation of concerns)

## Impact

- **Code**: Refactor engine.py to separate generation from presentation; move WindowInfo to domain.py; add DispatchContext to domain.py
- **API**: New generator-based API for Input Engine; new domain objects (WindowInfo, DispatchContext)
- **Dependencies**: None (uses Python standard library)
- **Systems**: Internal refactoring; no external systems affected
- **Breaking changes**: Input Engine API changes from run_engine() to read_events() generator
