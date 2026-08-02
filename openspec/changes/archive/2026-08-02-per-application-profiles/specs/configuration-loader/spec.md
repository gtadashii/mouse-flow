## MODIFIED Requirements

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
