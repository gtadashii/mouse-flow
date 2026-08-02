## Purpose

Loads user-defined configuration from YAML files, validates the configuration data, translates it into domain objects, and resolves which action matches a dispatched event context.

## Requirements

### Requirement: Configuration loading
The system SHALL load user-defined configuration from a YAML file during startup.

#### Scenario: Valid configuration file loaded
- **WHEN** a valid YAML configuration file exists at the expected path
- **THEN** the system loads the configuration and translates it into Profile domain objects

#### Scenario: Configuration file not found
- **WHEN** no configuration file exists at the expected path
- **THEN** the system reports that the configuration file is missing

#### Scenario: Configuration file is empty
- **WHEN** the configuration file exists but is empty
- **THEN** the system reports that the configuration is invalid

### Requirement: Configuration validation
The system SHALL validate the configuration data and report errors clearly.

#### Scenario: Valid configuration structure
- **WHEN** the configuration file contains valid structure with application profiles and mappings
- **THEN** the system accepts the configuration without errors

#### Scenario: Invalid action type
- **WHEN** the configuration contains an unrecognized action type
- **THEN** the system reports a validation error indicating the invalid action type

#### Scenario: Missing required fields
- **WHEN** the configuration is missing required fields (e.g., app_name, mappings)
- **THEN** the system reports a validation error indicating which fields are missing

#### Scenario: Invalid mapping format
- **WHEN** a mapping entry does not conform to the expected format
- **THEN** the system reports a validation error with details about the invalid mapping

### Requirement: Action resolution
The system SHALL resolve which action, if any, matches a dispatched event context using the profile selected by the profile resolution layer.

#### Scenario: Matching rule exists in selected profile
- **WHEN** a DispatchContext is provided
- **AND** the profile resolution layer selects a profile (application-specific or global)
- **AND** the selected profile contains a mapping for the event
- **THEN** the system returns the corresponding Action

#### Scenario: No mapping in selected profile
- **WHEN** a DispatchContext is provided
- **AND** the profile resolution layer selects a profile
- **AND** the selected profile does not contain a mapping for the event
- **THEN** the system reports that no action is configured

#### Scenario: No profile selected
- **WHEN** a DispatchContext is provided
- **AND** the profile resolution layer cannot select any profile (no application-specific or global profile exists)
- **THEN** the system reports that no action is configured

#### Scenario: Window info is null
- **WHEN** a DispatchContext is provided with null WindowInfo
- **THEN** the system reports that no action is configured

### Requirement: Resolved action production
The system SHALL produce a domain Action object when a matching rule exists.

#### Scenario: Keyboard shortcut action resolved
- **WHEN** a mapping matches and the action type is keyboard
- **THEN** the system produces an Action object with action_type KEYBOARD and the key combination payload

#### Scenario: Command action resolved
- **WHEN** a mapping matches and the action type is command
- **THEN** the system produces an Action object with action_type COMMAND and the command string payload

### Requirement: Missing configuration reporting
The system SHALL report when no action is configured for a given context.

#### Scenario: No action configured message
- **WHEN** no matching rule exists for a DispatchContext
- **THEN** the system reports that no action is configured, including the application name and event details

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
