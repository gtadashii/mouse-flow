## MODIFIED Requirements

### Requirement: Configuration loading with gesture support
The system SHALL load user-defined configuration from YAML files, validating the configuration data, translating it into domain objects, and resolving which action matches a dispatched event context, including gesture events.

#### Scenario: Valid configuration file with gestures loaded
- **WHEN** a valid YAML configuration file exists with gesture mappings
- **THEN** the system loads the configuration
- **AND** translates gesture mappings into Profile domain objects
- **AND** gesture directions are mapped to actions

#### Scenario: Gesture mapping validated
- **WHEN** the configuration contains a gesture mapping
- **AND** the gesture direction is valid (UP, DOWN, LEFT, RIGHT)
- **THEN** the system accepts the mapping
- **AND** creates an Action for the gesture

#### Scenario: Invalid gesture direction rejected
- **WHEN** the configuration contains a gesture mapping
- **AND** the gesture direction is not valid
- **THEN** the system reports a validation error
- **AND** indicates the invalid gesture direction

#### Scenario: Action resolution with gesture
- **WHEN** a DispatchContext contains a Gesture
- **AND** a Profile exists for the application
- **AND** the Profile contains a mapping for the gesture direction
- **THEN** the system returns the corresponding Action

#### Scenario: Action resolution with gesture but no mapping
- **WHEN** a DispatchContext contains a Gesture
- **AND** a Profile exists for the application
- **AND** the Profile does not contain a mapping for the gesture direction
- **THEN** the system reports that no action is configured

#### Scenario: Configuration format supports gestures
- **WHEN** the configuration file contains a gestures section
- **THEN** the system parses gesture-to-action mappings
- **AND** each mapping specifies a direction and an action
