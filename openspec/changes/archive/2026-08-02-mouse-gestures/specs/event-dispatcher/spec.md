## MODIFIED Requirements

### Requirement: Event dispatch with gesture support
The system SHALL dispatch events that include both mouse button events and recognized gestures, maintaining the existing pipeline flow.

#### Scenario: Mouse button event dispatched
- **WHEN** a mouse button is pressed or released
- **AND** gesture mode is not active
- **THEN** the system creates a DispatchContext with the MouseEvent
- **AND** the DispatchContext includes WindowInfo
- **AND** the DispatchContext enters the action resolution pipeline

#### Scenario: Gesture event dispatched
- **WHEN** a gesture is recognized and completed
- **THEN** the system creates a DispatchContext with the Gesture
- **AND** the DispatchContext includes WindowInfo
- **AND** the DispatchContext enters the action resolution pipeline

#### Scenario: Gesture button press does not dispatch
- **WHEN** a gesture button is pressed
- **THEN** gesture mode becomes active
- **AND** no DispatchContext is created for the button press
- **AND** pointer movement tracking begins

#### Scenario: Gesture button release without gesture does not dispatch
- **WHEN** gesture mode is active
- **AND** no gesture has been recognized
- **AND** the gesture button is released
- **THEN** no DispatchContext is created
- **AND** the system returns to normal event processing

#### Scenario: Window info included in gesture dispatch
- **WHEN** a gesture is recognized
- **THEN** the system queries the current window information
- **AND** the WindowInfo is included in the DispatchContext
- **AND** the DispatchContext flows through the existing pipeline
