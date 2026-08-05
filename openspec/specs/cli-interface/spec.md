## Purpose

Provides a command-line interface for users to inspect, diagnose, and operate MouseFlow without interacting directly with internal implementation details or infrastructure files.

## Requirements

### Requirement: CLI provides subcommand structure
The system SHALL provide a single entry point (`mouseflow`) with subcommands for different operations. The CLI SHALL support `start`, `status`, `devices`, `config show`, `config validate`, and `config reload` subcommands.

#### Scenario: User executes CLI without arguments
- **WHEN** user runs `mouseflow` without arguments
- **THEN** system displays help message listing available subcommands
- **THEN** system exits with non-zero status code

#### Scenario: User requests help
- **WHEN** user runs `mouseflow --help`
- **THEN** system displays help message with all available subcommands and options
- **THEN** system exits with zero status code

#### Scenario: User requests version
- **WHEN** user runs `mouseflow --version`
- **THEN** system displays version information
- **THEN** system exits with zero status code

### Requirement: CLI start command launches daemon
The system SHALL provide a `start` subcommand that launches the MouseFlow daemon in the foreground.

#### Scenario: User starts daemon
- **WHEN** user runs `mouseflow start`
- **THEN** system initializes all components and starts the event processing loop
- **THEN** daemon continues running until terminated by signal or error

### Requirement: CLI status command shows application state
The system SHALL provide a `status` subcommand that displays the current application state including running status, device connection, configuration status, and active profile.

#### Scenario: Daemon is running with active device
- **WHEN** user runs `mouseflow status`
- **WHEN** daemon is running with connected device
- **THEN** system displays "Running: yes"
- **THEN** system displays "Device: <device name>"
- **THEN** system displays "Configuration: loaded"
- **THEN** system displays "Active profile: <profile name or global>"
- **THEN** system exits with zero status code

#### Scenario: Daemon is not running
- **WHEN** user runs `mouseflow status`
- **WHEN** daemon is not running
- **THEN** system displays "Error: MouseFlow daemon is not running"
- **THEN** system displays hint to start daemon
- **THEN** system exits with non-zero status code

### Requirement: CLI devices command lists available devices
The system SHALL provide a `devices` subcommand that lists all supported mouse devices connected to the system, indicating which one is active.

#### Scenario: Multiple devices available
- **WHEN** user runs `mouseflow devices`
- **WHEN** multiple supported devices are connected
- **THEN** system displays list of devices with path, name, and active status
- **THEN** active device is marked with indicator
- **THEN** system exits with zero status code

#### Scenario: No devices available
- **WHEN** user runs `mouseflow devices`
- **WHEN** no supported devices are connected
- **THEN** system displays "No supported devices found"
- **THEN** system exits with zero status code

### Requirement: CLI config show displays loaded configuration
The system SHALL provide a `config show` subcommand that displays the currently loaded configuration including all profiles and their mappings.

#### Scenario: Configuration is loaded
- **WHEN** user runs `mouseflow config show`
- **WHEN** configuration is successfully loaded
- **THEN** system displays configuration in human-readable format
- **THEN** system shows all profiles and their input-to-action mappings
- **THEN** system exits with zero status code

#### Scenario: No configuration loaded
- **WHEN** user runs `mouseflow config show`
- **WHEN** no configuration is loaded
- **THEN** system displays "No configuration loaded"
- **THEN** system exits with zero status code

### Requirement: CLI config validate checks configuration file
The system SHALL provide a `config validate` subcommand that validates a configuration file without loading it into the running daemon.

#### Scenario: Valid configuration file
- **WHEN** user runs `mouseflow config validate`
- **WHEN** configuration file is valid
- **THEN** system displays "Configuration is valid"
- **THEN** system exits with zero status code

#### Scenario: Invalid configuration file
- **WHEN** user runs `mouseflow config validate`
- **WHEN** configuration file has errors
- **THEN** system displays "Configuration is invalid"
- **THEN** system displays list of validation errors
- **THEN** system exits with non-zero status code

#### Scenario: Configuration file not found
- **WHEN** user runs `mouseflow config validate`
- **WHEN** configuration file does not exist
- **THEN** system displays "Configuration file not found: <path>"
- **THEN** system exits with non-zero status code

### Requirement: CLI config reload refreshes configuration
The system SHALL provide a `config reload` subcommand that instructs the running daemon to reload its configuration from disk.

#### Scenario: Successful reload
- **WHEN** user runs `mouseflow config reload`
- **WHEN** daemon successfully reloads configuration
- **THEN** system displays "Configuration reloaded successfully"
- **THEN** system exits with zero status code

#### Scenario: Reload fails due to invalid configuration
- **WHEN** user runs `mouseflow config reload`
- **WHEN** configuration file is invalid
- **THEN** system displays "Configuration reload failed: <error message>"
- **THEN** daemon continues using previous configuration
- **THEN** system exits with non-zero status code

#### Scenario: Daemon not running
- **WHEN** user runs `mouseflow config reload`
- **WHEN** daemon is not running
- **THEN** system displays "Error: MouseFlow daemon is not running"
- **THEN** system exits with non-zero status code

### Requirement: CLI output is human-readable
The system SHALL format all command output to be concise, human-readable, and actionable. Error messages SHALL clearly explain the detected problem and suggest corrective action when possible.

#### Scenario: Error output includes actionable message
- **WHEN** command fails due to recoverable error
- **THEN** system displays clear error message
- **THEN** system suggests corrective action (e.g., "Start daemon with: mouseflow start")

#### Scenario: Success output is concise
- **WHEN** command succeeds
- **THEN** system displays relevant information only
- **THEN** system avoids unnecessary verbosity

### Requirement: CLI remains independent from business logic
The CLI SHALL NOT implement business rules, resolve actions, process input events, or interact directly with infrastructure beyond invoking application services via IPC.

#### Scenario: CLI delegates to services
- **WHEN** CLI command is executed
- **THEN** CLI parses arguments and validates input
- **THEN** CLI sends request to daemon via IPC
- **THEN** CLI formats and displays response
- **THEN** CLI does not implement business logic
