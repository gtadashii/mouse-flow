## 1. EventDispatcher Implementation

- [x] 1.1 Create `src/mouseflow/dispatcher.py` module
- [x] 1.2 Implement EventDispatcher class with WindowResolver dependency injection
- [x] 1.3 Implement `dispatch()` method that takes event generator and yields DispatchContext
- [x] 1.4 Handle window resolution failures gracefully (pass None to DispatchContext)
- [x] 1.5 Implement `format_dispatch_context()` function for human-readable output

## 2. Integration

- [x] 2.1 Update `__main__.py` to use EventDispatcher instead of direct read_events()
- [x] 2.2 Wire up read_events() generator and SwayResolver to EventDispatcher
- [x] 2.3 Replace window info display with dispatch context display
- [x] 2.4 Verify application still runs correctly end-to-end

## 3. Testing

- [x] 3.1 Write unit tests for EventDispatcher with mock WindowResolver
- [x] 3.2 Write unit tests for dispatch() method with various event scenarios
- [x] 3.3 Write unit tests for window resolution failure handling
- [x] 3.4 Write unit tests for format_dispatch_context()
- [x] 3.5 Write integration tests for full pipeline (Input Engine → Dispatcher → Output)
- [x] 3.6 Run all tests and verify 100% pass rate

## 4. Validation

- [x] 4.1 Run mypy type checking
- [x] 4.2 Run ruff linting
- [x] 4.3 Run ruff formatting
- [x] 4.4 Manually test with real mouse device (optional)
