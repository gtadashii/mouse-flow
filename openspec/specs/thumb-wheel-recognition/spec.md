## Purpose

Recognizes horizontal thumb wheel movement from raw device events, determines direction, and produces dedicated thumb wheel UserInput domain objects for the action resolution pipeline.

## Requirements

### Requirement: Thumb wheel event recognition
The system SHALL recognize horizontal thumb wheel interactions from the input device.

#### Scenario: Thumb wheel scrolled right
- **WHEN** the user scrolls the thumb wheel to the right
- **THEN** the system produces a UserInput with identifier THUMB_WHEEL_RIGHT

#### Scenario: Thumb wheel scrolled left
- **WHEN** the user scrolls the thumb wheel to the left
- **THEN** the system produces a UserInput with identifier THUMB_WHEEL_LEFT

### Requirement: Thumb wheel direction detection
The system SHALL determine the direction of thumb wheel movement based on the event value.

#### Scenario: Positive value indicates right direction
- **WHEN** a thumb wheel event has a positive value
- **THEN** the system identifies the direction as right

#### Scenario: Negative value indicates left direction
- **WHEN** a thumb wheel event has a negative value
- **THEN** the system identifies the direction as left

### Requirement: Thumb wheel continuous processing
The system SHALL process thumb wheel movement as a continuous interaction without blocking.

#### Scenario: Rapid thumb wheel scrolling
- **WHEN** the user scrolls the thumb wheel rapidly in succession
- **THEN** the system processes each movement event independently and remains responsive

#### Scenario: Thumb wheel during normal operation
- **WHEN** the user scrolls the thumb wheel while the application is processing other inputs
- **THEN** the system handles thumb wheel events without interrupting normal execution

### Requirement: Thumb wheel separation from gestures
The system SHALL produce thumb wheel identifiers that are distinct from gesture identifiers.

#### Scenario: Thumb wheel does not produce gesture identifiers
- **WHEN** a thumb wheel event is processed
- **THEN** the resulting UserInput identifier is THUMB_WHEEL_LEFT or THUMB_WHEEL_RIGHT, not GESTURE_LEFT or GESTURE_RIGHT

### Requirement: Thumb wheel pipeline integration
Thumb wheel UserInput objects SHALL participate in the existing action resolution pipeline.

#### Scenario: Thumb wheel action resolved
- **WHEN** a thumb wheel UserInput enters the pipeline
- **THEN** the system resolves the configured action for the active application using the thumb wheel identifier

#### Scenario: Thumb wheel with no mapping
- **WHEN** a thumb wheel UserInput enters the pipeline and no action is configured for the identifier
- **THEN** the system does not execute any action and continues processing
