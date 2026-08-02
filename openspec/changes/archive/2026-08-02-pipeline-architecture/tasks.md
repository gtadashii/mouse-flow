## 1. Domain Model Enhancements

- [x] 1.1 Move WindowInfo from resolver.py to domain.py
- [x] 1.2 Add DispatchContext dataclass to domain.py
- [x] 1.3 Update imports in resolver.py to use domain.WindowInfo
- [x] 1.4 Update tests for WindowInfo to use domain module

## 2. Input Engine Refactoring

- [x] 2.1 Create read_events(device_path) generator function
- [x] 2.2 Refactor run_engine() to use read_events() internally
- [x] 2.3 Update tests to use new generator-based API
- [x] 2.4 Verify existing tests still pass

## 3. Pipeline Integration

- [x] 3.1 Update __main__.py to demonstrate pipeline usage
- [x] 3.2 Add integration tests for pipeline stages
- [x] 3.3 Verify all tests pass (unit + integration)
