## MODIFIED Requirements

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

#### Scenario: Horizontal thumb wheel scrolled right
- **WHEN** the user scrolls the thumb wheel to the right (REL_HWHEEL with positive value)
- **THEN** the system displays "THUMB_WHEEL_RIGHT"

#### Scenario: Horizontal thumb wheel scrolled left
- **WHEN** the user scrolls the thumb wheel to the left (REL_HWHEEL with negative value)
- **THEN** the system displays "THUMB_WHEEL_LEFT"

#### Scenario: Unsupported event received
- **WHEN** an event not in the supported list is received
- **THEN** the system ignores it without interrupting execution
