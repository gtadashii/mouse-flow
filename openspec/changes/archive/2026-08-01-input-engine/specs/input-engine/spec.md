## Purpose

Establishes a continuous stream of input events from the selected mouse device, enabling real-time event reporting as the foundation for future event processing and action execution.

## ADDED Requirements

### Requirement: Continuous event stream
The system SHALL establish and maintain a continuous stream of input events from the selected device.

#### Scenario: Device opened successfully
- **WHEN** the application starts with a valid device
- **THEN** the system opens the device and begins receiving events

#### Scenario: Device unavailable at startup
- **WHEN** the selected device cannot be opened
- **THEN** the system reports the error and exits

### Requirement: Supported event recognition
The system SHALL recognize and report supported mouse events.

#### Scenario: Side button pressed
- **WHEN** the user presses BTN_SIDE
- **THEN** the system displays "BTN_SIDE"

#### Scenario: Extra button pressed
- **WHEN** the user presses BTN_EXTRA
- **THEN** the system displays "BTN_EXTRA"

#### Scenario: Forward button pressed
- **WHEN** the user presses BTN_FORWARD
- **THEN** the system displays "BTN_FORWARD"

#### Scenario: Horizontal wheel scrolled
- **WHEN** the user scrolls REL_HWHEEL
- **THEN** the system displays "REL_HWHEEL"

#### Scenario: Unsupported event received
- **WHEN** an event not in the supported list is received
- **THEN** the system ignores it without interrupting execution

### Requirement: Real-time event display
The system SHALL display each supported event immediately after it is received.

#### Scenario: Event displayed
- **WHEN** a supported event is received
- **THEN** the event name is printed to standard output

### Requirement: Continuous execution
The system SHALL continue processing events until interrupted by the user.

#### Scenario: Application remains active
- **WHEN** no events are being received
- **THEN** the application remains responsive and waiting

#### Scenario: Long-running execution
- **WHEN** the application runs for an extended period
- **THEN** it continues to process events without degradation

### Requirement: Graceful shutdown
The system SHALL terminate cleanly when interrupted, releasing all resources.

#### Scenario: User interrupts with Ctrl+C
- **WHEN** the user sends SIGINT (Ctrl+C)
- **THEN** the system closes the device handle and exits cleanly

#### Scenario: Resources released
- **WHEN** the application exits
- **THEN** no file descriptors or device handles remain open
