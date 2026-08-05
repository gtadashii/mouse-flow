## Purpose

Defines the core domain objects that represent the fundamental concepts of MouseFlow, providing a shared vocabulary and type-safe API for all components to communicate.

## Requirements

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

### Requirement: Window information representation
The system SHALL provide an immutable object representing the active window, combining application and window details.

#### Scenario: Window info created with application and window
- **WHEN** the system identifies the focused window
- **THEN** the system creates a window info object containing the application and window objects

#### Scenario: Window info with unknown application
- **WHEN** the application name cannot be determined
- **THEN** the system creates a window info object with an Application object having "Unknown" as the name

#### Scenario: Window info with untitled window
- **WHEN** the window title cannot be determined
- **THEN** the system creates a window info object with a Window object having "Untitled" as the title

### Requirement: Window info immutability
The window info object SHALL be immutable after creation.

#### Scenario: Attempt to modify window info
- **WHEN** code attempts to modify a window info object's attributes
- **THEN** the system raises an error preventing the modification

### Requirement: Window info equality
Window info objects with identical values SHALL be considered equal.

#### Scenario: Equal window info objects
- **WHEN** two window info objects have the same application and window
- **THEN** the objects are considered equal

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

### Requirement: Gesture representation
The system SHALL provide immutable domain objects representing mouse gestures.

#### Scenario: Gesture direction enum exists
- **WHEN** the domain model is loaded
- **THEN** a GestureDirection enum exists with values: UP, DOWN, LEFT, RIGHT

#### Scenario: Gesture object created
- **WHEN** a gesture is recognized
- **THEN** the system creates a Gesture domain object
- **AND** the object contains the direction (GestureDirection)
- **AND** the object is immutable

#### Scenario: Gesture object equality
- **WHEN** two Gesture objects have the same direction
- **THEN** the objects are considered equal

### Requirement: Thumb wheel input identifiers
The system SHALL provide distinct input identifiers for thumb wheel directions.

#### Scenario: Thumb wheel left identifier exists
- **WHEN** the domain model is loaded
- **THEN** InputIdentifier contains the value THUMB_WHEEL_LEFT

#### Scenario: Thumb wheel right identifier exists
- **WHEN** the domain model is loaded
- **THEN** InputIdentifier contains the value THUMB_WHEEL_RIGHT

#### Scenario: Thumb wheel identifiers are distinct from gesture identifiers
- **WHEN** the domain model is loaded
- **THEN** THUMB_WHEEL_LEFT and THUMB_WHEEL_RIGHT are separate enum values from GESTURE_LEFT and GESTURE_RIGHT
