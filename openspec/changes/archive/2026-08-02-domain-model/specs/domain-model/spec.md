## Purpose

Defines the core domain objects that represent the fundamental concepts of MouseFlow, providing a shared vocabulary and type-safe API for all components to communicate.

## ADDED Requirements

### Requirement: Mouse event representation
The system SHALL provide an immutable object representing a mouse event with its type and value.

#### Scenario: Button event created
- **WHEN** a mouse button is pressed or released
- **THEN** the system creates a mouse event object containing the button identifier and press/release state

#### Scenario: Wheel event created
- **WHEN** the mouse wheel is scrolled
- **THEN** the system creates a mouse event object containing the wheel axis and movement value

### Requirement: Application representation
The system SHALL provide an immutable object representing the active application.

#### Scenario: Application object created
- **WHEN** the system identifies the focused application
- **THEN** the system creates an application object containing the application name

#### Scenario: Unknown application
- **WHEN** the application name cannot be determined
- **THEN** the system creates an application object with "Unknown" as the name

### Requirement: Window representation
The system SHALL provide an immutable object representing the active window.

#### Scenario: Window object created
- **WHEN** the system identifies the focused window
- **THEN** the system creates a window object containing the window title

#### Scenario: Untitled window
- **WHEN** the window title cannot be determined
- **THEN** the system creates a window object with "Untitled" as the title

### Requirement: Action representation
The system SHALL provide an immutable object representing an executable action.

#### Scenario: Keyboard shortcut action
- **WHEN** an action is defined as a keyboard shortcut
- **THEN** the system creates an action object containing the key combination

#### Scenario: Command action
- **WHEN** an action is defined as a shell command
- **THEN** the system creates an action object containing the command string

### Requirement: Profile representation
The system SHALL provide an immutable object representing an application profile.

#### Scenario: Profile with mappings
- **WHEN** a profile is defined for an application
- **THEN** the system creates a profile object containing the application identifier and its action mappings

#### Scenario: Empty profile
- **WHEN** a profile has no action mappings defined
- **THEN** the system creates a profile object with an empty mapping set

### Requirement: Domain object immutability
All domain objects SHALL be immutable after creation.

#### Scenario: Attempt to modify domain object
- **WHEN** code attempts to modify a domain object's attributes
- **THEN** the system raises an error preventing the modification

### Requirement: Domain object equality
Domain objects with identical values SHALL be considered equal.

#### Scenario: Equal mouse events
- **WHEN** two mouse event objects have the same button and state
- **THEN** the objects are considered equal

#### Scenario: Equal applications
- **WHEN** two application objects have the same name
- **THEN** the objects are considered equal
