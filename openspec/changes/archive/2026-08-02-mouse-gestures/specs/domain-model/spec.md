## MODIFIED Requirements

### Requirement: Domain object representation
The system SHALL provide immutable domain objects representing all core business concepts, including mouse events, window information, actions, profiles, and gestures.

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

#### Scenario: MouseEvent remains unchanged
- **WHEN** a mouse button is pressed or released
- **THEN** the system creates a MouseEvent domain object
- **AND** the object contains button, wheel, and value information

#### Scenario: Action object remains unchanged
- **WHEN** an action is defined
- **THEN** the system creates an Action domain object
- **AND** the object contains action_type and payload

#### Scenario: Profile object remains unchanged
- **WHEN** a profile is defined for an application
- **THEN** the system creates a Profile domain object
- **AND** the object contains app_name and mappings
