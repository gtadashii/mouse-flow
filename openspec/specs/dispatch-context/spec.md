## Purpose

Defines the DispatchContext domain object that combines mouse events with window information, serving as the unified context produced by the Event Dispatcher for downstream consumption.

## Requirements

### Requirement: Dispatch context representation
The system SHALL provide an immutable object that combines a mouse event with window information.

#### Scenario: Dispatch context created with mouse event and window info
- **WHEN** the Event Dispatcher receives a mouse event and resolves the active window
- **THEN** the system creates a dispatch context object containing both the mouse event and the window information

#### Scenario: Dispatch context created with null window info
- **WHEN** the Event Dispatcher receives a mouse event but window resolution fails
- **THEN** the system creates a dispatch context object with the mouse event and a null window info

### Requirement: Dispatch context immutability
The dispatch context object SHALL be immutable after creation.

#### Scenario: Attempt to modify dispatch context
- **WHEN** code attempts to modify a dispatch context object's attributes
- **THEN** the system raises an error preventing the modification

### Requirement: Dispatch context equality
Dispatch context objects with identical values SHALL be considered equal.

#### Scenario: Equal dispatch contexts
- **WHEN** two dispatch context objects have the same mouse event and window info
- **THEN** the objects are considered equal
