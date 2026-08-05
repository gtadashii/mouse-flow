## 1. Logging Infrastructure

- [x] 1.1 Write tests for logging configuration in daemon module
- [x] 1.2 Implement logging configuration function in `daemon.py` (setup_logging)
- [x] 1.3 Replace `print()` calls in `discovery.py` with logging
- [x] 1.4 Replace `print()` calls in `dispatcher.py` with logging
- [x] 1.5 Replace `print()` calls in `loader.py` with logging
- [x] 1.6 Replace `print()` calls in `runner.py` with logging
- [x] 1.7 Replace `print()` calls in `__main__.py` with logging
- [x] 1.8 Verify all tests pass with logging changes

## 2. Daemon Component - Core Lifecycle

- [x] 2.1 Write tests for daemon startup sequence (discovery, config, pipeline start)
- [x] 2.2 Implement daemon startup logic in `daemon.py` (start function)
- [x] 2.3 Write tests for daemon shutdown sequence (resource cleanup)
- [x] 2.4 Implement daemon shutdown logic in `daemon.py` (stop function)
- [x] 2.5 Write tests for complete daemon lifecycle (start → run → stop)
- [x] 2.6 Implement main daemon loop in `daemon.py` (run function)
- [x] 2.7 Verify all tests pass

## 3. Signal Handling

- [x] 3.1 Write tests for SIGTERM handling (graceful shutdown)
- [x] 3.2 Write tests for SIGINT handling (graceful shutdown)
- [x] 3.3 Implement signal handlers in `daemon.py`
- [x] 3.4 Verify signal handling works during event processing
- [x] 3.5 Verify all tests pass

## 4. Resource Management

- [x] 4.1 Write tests for evdev device cleanup on shutdown
- [x] 4.2 Write tests for i3ipc connection cleanup on shutdown
- [x] 4.3 Implement context managers or try/finally blocks for resource cleanup
- [x] 4.4 Verify resources are released even on unexpected errors
- [x] 4.5 Verify all tests pass

## 5. Entry Point Refactoring

- [x] 5.1 Update `__main__.py` to delegate to daemon.run()
- [x] 5.2 Verify application starts correctly via `uv run mouseflow`
- [x] 5.3 Verify application shuts down gracefully on Ctrl+C
- [x] 5.4 Verify all tests pass

## 6. systemd Service Integration

- [x] 6.1 Create `packaging/mouseflow.service` systemd user service unit
- [x] 6.2 Test service installation and enablement
- [x] 6.3 Test automatic startup on user login
- [x] 6.4 Test service stop and restart behavior
- [x] 6.5 Verify service status reporting works correctly

## 7. Failure Handling

- [x] 7.1 Write tests for device disconnection during operation
- [x] 7.2 Write tests for compositor connection loss
- [x] 7.3 Implement graceful termination on critical failures
- [x] 7.4 Verify appropriate error logging on failures
- [x] 7.5 Verify all tests pass

## 8. Documentation

- [x] 8.1 Update `docs/architecture.md` with daemon component section
- [x] 8.2 Update dependency graph in architecture.md
- [x] 8.3 Add systemd service installation instructions to README
- [x] 8.4 Create ADR for daemon lifecycle decision

## 9. Integration Testing

- [x] 9.1 Test complete startup sequence (service enable → login → running)
- [x] 9.2 Test graceful shutdown via systemctl stop
- [x] 9.3 Test graceful shutdown via SIGTERM
- [x] 9.4 Test graceful shutdown via SIGINT (Ctrl+C)
- [x] 9.5 Test resource cleanup verification (no open file descriptors)
- [x] 9.6 Test automatic restart on failure
- [x] 9.7 Verify long-running stability (no memory leaks, no degradation)

## 10. Quality Gates

- [x] 10.1 Run full test suite (pytest)
- [x] 10.2 Run linter (ruff)
- [x] 10.3 Run type checker (mypy)
- [x] 10.4 Run pre-commit hooks
- [x] 10.5 Verify CI pipeline passes
