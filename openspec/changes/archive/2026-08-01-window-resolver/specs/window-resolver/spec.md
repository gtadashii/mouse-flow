## Purpose

Identifies the currently focused window and extracts application name and window title, enabling MouseFlow to provide application-specific behavior based on where the user is working.

## ADDED Requirements

### Requirement: Active window resolution
The system SHALL determine which window currently has focus.

#### Scenario: Window with focus exists
- **WHEN** the system queries the active window
- **THEN** the system returns information about the currently focused window

#### Scenario: No window has focus
- **WHEN** no window currently has focus (e.g., desktop is focused)
- **THEN** the system reports that no application window is active

### Requirement: Application identification
The system SHALL extract and expose the application identifier from the focused window.

#### Scenario: Application name available
- **WHEN** the focused window has an associated application name
- **THEN** the system returns the application name (e.g., "Firefox", "Code")

#### Scenario: Application name unavailable
- **WHEN** the focused window does not have an application name
- **THEN** the system returns "Unknown" or an empty string

### Requirement: Window title extraction
The system SHALL extract and expose the window title from the focused window.

#### Scenario: Window title available
- **WHEN** the focused window has a title
- **THEN** the system returns the window title (e.g., "ChatGPT", "README.md")

#### Scenario: Window title unavailable
- **WHEN** the focused window does not have a title
- **THEN** the system returns "Untitled" or an empty string

### Requirement: User feedback presentation
The system SHALL present resolved window information in a human-readable format.

#### Scenario: Display active window information
- **WHEN** the system resolves the active window
- **THEN** the system displays the application name and window title

#### Scenario: Display format
- **WHEN** displaying window information
- **THEN** the output follows the format: "Application\n<name>\n\nTitle\n<title>"

### Requirement: Graceful failure handling
The system SHALL handle failures without crashing.

#### Scenario: Window manager unavailable
- **WHEN** the window manager cannot be queried
- **THEN** the system reports an error and exits gracefully

#### Scenario: Permission denied
- **WHEN** the system lacks permissions to query window information
- **THEN** the system reports a permission error and exits gracefully

### Requirement: Compositor independence
The system SHALL isolate window resolution logic to support future compositor integrations.

#### Scenario: Sway compositor
- **WHEN** running under Sway
- **THEN** the system uses Sway IPC to query window information

#### Scenario: Future compositor support
- **WHEN** a new compositor backend is added
- **THEN** the window resolver interface remains unchanged
