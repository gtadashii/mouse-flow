## Context

See proposal.md for motivation. The pipeline architecture is now in place: Input Engine produces MouseEvent objects via `read_events()` generator, Window Resolver provides WindowInfo via `WindowResolver` protocol, and DispatchContext domain object exists to combine both. The Event Dispatcher will be the first orchestration component that ties these pieces together.

## Goals / Non-Goals

**Goals:**
- Create EventDispatcher as a thin orchestration layer
- EventDispatcher consumes MouseEvent generator and produces DispatchContext generator
- EventDispatcher depends on WindowResolver protocol (dependency injection)
- Each event triggers a fresh window resolution (no caching)
- Integrate EventDispatcher into the main application loop
- Display DispatchContext in human-readable format

**Non-Goals:**
- Implement configuration lookup (Sprint 6)
- Implement action resolution or execution (Sprint 7)
- Implement event caching or batching
- Implement gesture recognition
- Optimize window resolution performance (deferred until needed)

## Decisions

### Decision 1: EventDispatcher as generator wrapper

**Choice:** EventDispatcher exposes a `dispatch()` method that returns `Generator[DispatchContext]`, wrapping the input event generator.

**Rationale:**
- Consistent with `read_events()` generator pattern
- Lazy evaluation: window resolution happens only when events occur
- Natural fit for continuous event streams
- Easy to compose: `dispatcher.dispatch(read_events(path))`
- Allows downstream consumers to iterate naturally

**Alternatives considered:**
- Callback-based: `dispatcher.on_event(callback)` - harder to compose, less Pythonic
- Blocking method: `dispatcher.run()` - mixes orchestration with event loop control
- Batch processing: process multiple events at once - unnecessary complexity for current scope

### Decision 2: WindowResolver dependency injection

**Choice:** EventDispatcher receives a `WindowResolver` instance via constructor, not a concrete implementation.

**Rationale:**
- Follows dependency inversion principle
- Easy to test with mock resolvers
- Allows future compositor backends without changing EventDispatcher
- Consistent with existing WindowResolver protocol

**Alternatives considered:**
- Hard-code SwayResolver: Breaks compositor independence
- Global resolver instance: Harder to test, hidden dependencies
- Factory pattern: Overkill for single resolver type

### Decision 3: Window resolution per event

**Choice:** Call `resolver.resolve()` for each MouseEvent, no caching.

**Rationale:**
- Simplest implementation
- Window focus can change rapidly; stale data is worse than no data
- Resolution latency is acceptable for current use case
- Can optimize later if needed (cache with TTL, debounce, etc.)

**Alternatives considered:**
- Cache last WindowInfo: Risk of stale data, adds complexity
- Resolve once at startup: Incorrect behavior when windows change
- Background resolution thread: Over-engineering for current scope

### Decision 4: Null WindowInfo handling

**Choice:** DispatchContext allows `window_info: WindowInfo | None`, EventDispatcher passes None when resolution fails.

**Rationale:**
- Graceful degradation: events still processed even if window resolution fails
- Downstream components can decide how to handle missing context
- Consistent with DispatchContext domain object design

**Alternatives considered:**
- Skip events when resolution fails: Loses valid mouse events
- Raise exception: Breaks event stream, poor user experience
- Default "Unknown" WindowInfo: Hides resolution failures

### Decision 5: Display formatting

**Choice:** Add `format_dispatch_context()` function in dispatcher module, called from `__main__.py`.

**Rationale:**
- Separates formatting from orchestration logic
- Consistent with existing `format_found()`, `format_window_info()` pattern
- Easy to test formatting independently

**Alternatives considered:**
- Format inside EventDispatcher: Mixes concerns
- Format in __main__.py directly: Duplicates formatting logic
- Use DispatchContext.__str__(): Less control over format

## Risks / Trade-offs

**[Risk] Window resolution latency** → Each event triggers IPC call to Sway. If resolution is slow, events may queue up.
→ **Mitigation:** Current resolution is fast (<10ms). Monitor and optimize if needed (cache, async, etc.).

**[Risk] Window resolution failures** → Sway IPC may fail temporarily (socket issues, etc.).
→ **Mitigation:** EventDispatcher catches exceptions and passes None. User sees events without window info. Can add retry logic later if needed.

**[Risk] Tight coupling to WindowResolver protocol** → If protocol changes, EventDispatcher must change.
→ **Mitigation:** Protocol is stable and minimal. Changes would be breaking anyway. Acceptable risk.

**[Trade-off] No window caching** → More IPC calls than necessary if window doesn't change often.
→ **Acceptable because:** Simplicity > optimization at this stage. Can add caching later if profiling shows it's needed.
