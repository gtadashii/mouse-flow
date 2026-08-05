## 1. Operational Domain Objects

- [x] 1.1 Create operational domain objects in `domain.py`: DeviceInfo, ApplicationStatus, ValidationResult, ReloadResult
- [x] 1.2 Add unit tests for operational domain objects (creation, immutability, equality)

## 2. Service Layer

- [x] 2.1 Create `services.py` module with ApplicationServices class
- [x] 2.2 Implement `list_devices()` method that wraps DeviceDiscovery
- [x] 2.3 Implement `get_status()` method that returns ApplicationStatus
- [x] 2.4 Implement `get_configuration()` method that returns Configuration
- [x] 2.5 Implement `validate_configuration(path)` method that validates config file
- [x] 2.6 Implement `reload_configuration()` method that reloads config at runtime
- [x] 2.7 Add unit tests for Service Layer with mocked components

## 3. IPC Communication

- [x] 3.1 Create `ipc.py` module with IPCServer class
- [x] 3.2 Implement Unix socket server with JSON protocol
- [x] 3.3 Implement request dispatching to Service Layer methods
- [x] 3.4 Implement response serialization (domain objects to JSON)
- [x] 3.5 Add concurrent connection handling (thread per connection)
- [x] 3.6 Implement socket file lifecycle management (create, cleanup)
- [x] 3.7 Create IPCClient class for CLI to connect to daemon
- [x] 3.8 Add unit tests for IPC server and client with mocked services

## 4. Daemon Modifications

- [x] 4.1 Modify Daemon to create ApplicationServices instance during initialization
- [x] 4.2 Add IPC server startup in separate thread
- [x] 4.3 Implement thread-safe configuration reload with threading.Lock
- [x] 4.4 Add graceful IPC server shutdown in daemon shutdown sequence
- [x] 4.5 Update daemon unit tests for IPC server and config reload

## 5. CLI Component

- [x] 5.1 Create `cli.py` module with argparse-based command parser
- [x] 5.2 Implement `start` subcommand that launches daemon
- [x] 5.3 Implement `status` subcommand that queries daemon via IPC
- [x] 5.4 Implement `devices` subcommand that lists devices via IPC
- [x] 5.5 Implement `config show` subcommand that displays configuration
- [x] 5.6 Implement `config validate` subcommand that validates config file
- [x] 5.7 Implement `config reload` subcommand that triggers reload via IPC
- [x] 5.8 Add output formatting functions for human-readable results
- [x] 5.9 Add error handling for daemon not running scenarios
- [x] 5.10 Add unit tests for CLI with mocked IPC client

## 6. Entry Point Refactoring

- [x] 6.1 Refactor `__main__.py` to use CLI entry point
- [x] 6.2 Update `pyproject.toml` entry point to `mouseflow.cli:main`
- [x] 6.3 Verify `mouseflow --help` displays all subcommands
- [x] 6.4 Verify `mouseflow --version` displays version

## 7. Systemd Integration

- [x] 7.1 Update `packaging/mouseflow.service` to use `mouseflow start`
- [x] 7.2 Test systemd service startup and shutdown
- [x] 7.3 Verify signal handling still works with new entry point

## 8. Integration Testing

- [x] 8.1 Create integration test for full CLI workflow (start daemon, run commands)
- [x] 8.2 Test concurrent CLI commands against running daemon
- [x] 8.3 Test configuration reload with valid and invalid files
- [x] 8.4 Test error scenarios (daemon not running, invalid config, etc.)

## 9. Documentation

- [x] 9.1 Update README.md with CLI usage examples
- [x] 9.2 Add CLI command reference documentation
- [x] 9.3 Update architecture.md (already done in architecture evolution review)

## 10. Quality Checks

- [x] 10.1 Run linter and fix any issues
- [x] 10.2 Run type checker and fix any issues
- [x] 10.3 Run all tests and ensure 100% pass rate
- [x] 10.4 Verify code coverage for new modules
- [x] 10.5 Run pre-commit hooks
