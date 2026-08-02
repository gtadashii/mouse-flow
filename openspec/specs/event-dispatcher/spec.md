## Purpose

Orchestrates the combination of mouse events with window information, producing unified DispatchContext objects that downstream components can consume without needing to coordinate multiple data sources.

## Requirements

### Requirement: Event reception
The system SHALL receive mouse events from the Input Engine as domain MouseEvent objects.

#### Scenario: Mouse event received
- **WHEN** the Input Engine produces a MouseEvent
- **THEN** the Event Dispatcher receives the event for processing

#### Scenario: Unsupported event filtered
- **WHEN** the Input Engine produces an unsupported event
- **THEN** the Event Dispatcher does not receive the event

### Requirement: Window resolution per event
The system SHALL obtain the current window information for each received mouse event.

#### Scenario: Window resolution succeeds
- **WHEN** the Event Dispatcher receives a MouseEvent
- **THEN** the Event Dispatcher requests the current WindowInfo from the Window Resolver
- **AND** the WindowInfo is included in the resulting DispatchContext

#### Scenario: Window resolution fails
- **WHEN** the Event Dispatcher receives a MouseEvent
- **AND** the Window Resolver cannot determine the active window
- **THEN** the Event Dispatcher creates a DispatchContext with null WindowInfo

### Requirement: Dispatch context creation
The system SHALL create a DispatchContext combining the MouseEvent and WindowInfo.

#### Scenario: Context created with window info
- **WHEN** the Event Dispatcher receives a MouseEvent and obtains WindowInfo
- **THEN** the system creates a DispatchContext containing both the event and window info

#### Scenario: Context created without window info
- **WHEN** the Event Dispatcher receives a MouseEvent but window resolution fails
- **THEN** the system creates a DispatchContext containing the event with null window info

### Requirement: Event independence
The system SHALL process each mouse event independently without maintaining state.

#### Scenario: Sequential events processed independently
- **WHEN** multiple mouse events occur in sequence
- **THEN** each event is processed independently
- **AND** no event history is maintained between dispatches

### Requirement: Infrastructure independence
The Event Dispatcher SHALL depend only on domain abstractions, not infrastructure details.

#### Scenario: Dispatcher uses domain objects only
- **WHEN** the Event Dispatcher processes events
- **THEN** it uses only MouseEvent, WindowInfo, and DispatchContext domain objects
- **AND** it does not directly interact with evdev, i3ipc, or other infrastructure

#### Scenario: Dispatcher uses WindowResolver protocol
- **WHEN** the Event Dispatcher needs window information
- **THEN** it depends on the WindowResolver protocol abstraction
- **AND** it does not depend on specific implementations like SwayResolver

### Requirement: Gesture event dispatch
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
