## Purpose

Executes resolved actions on the operating system, including keyboard shortcuts, shell commands, and application launches. Reports execution results and handles failures gracefully without affecting the event pipeline.

## Requirements

### Requirement: Keyboard action execution
The system SHALL execute keyboard shortcuts configured for mouse events.

#### Scenario: Keyboard shortcut executed successfully
- **WHEN** a keyboard action is resolved for a mouse event
- **THEN** the system simulates the configured key combination
- **AND** the operating system receives the key press events

#### Scenario: Complex key combination
- **WHEN** a keyboard action with modifiers (e.g., Ctrl+Shift+P) is resolved
- **THEN** the system simulates the modifier keys and main key in the correct order
- **AND** the key combination is executed as a single atomic action

### Requirement: Shell command execution
The system SHALL execute shell commands configured for mouse events.

#### Scenario: Shell command executed successfully
- **WHEN** a command action is resolved for a mouse event
- **THEN** the system executes the configured shell command
- **AND** the command runs in the user's shell environment

#### Scenario: Command with arguments
- **WHEN** a command action with arguments (e.g., "swaymsg workspace next") is resolved
- **THEN** the system executes the command with all arguments
- **AND** the command completes execution

### Requirement: Application launch execution
The system SHALL launch applications configured for mouse events.

#### Scenario: Application launched successfully
- **WHEN** an application launch action is resolved for a mouse event
- **THEN** the system starts the configured application
- **AND** the application process is created

### Requirement: Execution result reporting
The system SHALL report the result of action execution.

#### Scenario: Successful execution reported
- **WHEN** an action is executed successfully
- **THEN** the system reports the action and its execution status
- **AND** the report includes the application name, event, action, and status

#### Scenario: Execution failure reported
- **WHEN** an action fails to execute
- **THEN** the system reports the failure
- **AND** the report includes error details

### Requirement: Graceful failure handling
The system SHALL handle execution failures without terminating the application.

#### Scenario: Execution failure does not terminate application
- **WHEN** an action fails to execute (e.g., command not found, permission denied)
- **THEN** the system reports the failure
- **AND** the application continues processing future events
- **AND** the event pipeline remains responsive

#### Scenario: Repeated failures handled gracefully
- **WHEN** multiple actions fail in sequence
- **THEN** each failure is reported independently
- **AND** the application remains stable and responsive

### Requirement: Execution isolation
The system SHALL isolate action execution from the event processing pipeline.

#### Scenario: Long-running command does not block events
- **WHEN** a shell command takes time to execute
- **THEN** the event pipeline continues processing new events
- **AND** the application remains responsive

#### Scenario: Action execution error does not affect pipeline
- **WHEN** an action execution raises an exception
- **THEN** the exception is caught and reported
- **AND** the event pipeline continues normally
