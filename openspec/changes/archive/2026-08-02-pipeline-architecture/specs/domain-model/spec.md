## MODIFIED Requirements

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
