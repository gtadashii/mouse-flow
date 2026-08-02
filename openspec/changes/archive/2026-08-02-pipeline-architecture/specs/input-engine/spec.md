## MODIFIED Requirements

### Requirement: Event stream generation
The system SHALL provide a generator-based API that yields domain mouse events from the input device.

#### Scenario: Event stream yields mouse events
- **WHEN** the input engine reads from a supported device
- **THEN** the system yields MouseEvent domain objects for each supported hardware event

#### Scenario: Event stream filters unsupported events
- **WHEN** the input device produces an unsupported event
- **THEN** the system does not yield that event

#### Scenario: Event stream handles device disconnection
- **WHEN** the input device becomes unavailable
- **THEN** the system raises an appropriate error

### Requirement: Event stream separation from presentation
The input engine SHALL NOT be responsible for displaying or formatting events.

#### Scenario: Input engine produces domain objects only
- **WHEN** the input engine processes hardware events
- **THEN** the engine yields domain objects without any console output or formatting
