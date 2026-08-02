## Purpose

Selects the appropriate profile (application-specific or global) based on the focused application, applying deterministic precedence rules and providing fallback behavior when no application-specific profile exists.

## Requirements

### Requirement: Application-specific profile selection
The system SHALL select the application-specific profile when one exists for the focused application.

#### Scenario: Matching application profile exists
- **WHEN** a mouse event occurs in an application
- **AND** an application-specific profile exists for that application
- **THEN** the system selects the application-specific profile for action resolution

#### Scenario: Application profile selected over global
- **WHEN** both an application-specific profile and a global profile exist
- **AND** the focused application matches the application-specific profile
- **THEN** the system selects the application-specific profile, not the global profile

### Requirement: Global profile fallback
The system SHALL use the global profile when no application-specific profile matches the focused application.

#### Scenario: No matching application profile
- **WHEN** a mouse event occurs in an application
- **AND** no application-specific profile exists for that application
- **AND** a global profile exists
- **THEN** the system selects the global profile for action resolution

#### Scenario: Global profile used for unknown application
- **WHEN** a mouse event occurs in an unknown or unrecognized application
- **AND** a global profile exists
- **THEN** the system selects the global profile for action resolution

### Requirement: Deterministic precedence
Profile selection SHALL follow deterministic precedence rules where application-specific profiles always take priority over the global profile.

#### Scenario: Precedence is consistent
- **WHEN** profile resolution is performed multiple times with the same context
- **THEN** the same profile is selected each time

#### Scenario: Application-specific always wins
- **WHEN** an application-specific profile exists for the focused application
- **THEN** the global profile is never selected, regardless of global profile contents

### Requirement: Profile selection reporting
The system SHALL report which profile was selected during action resolution.

#### Scenario: Application profile selection reported
- **WHEN** an application-specific profile is selected
- **THEN** the system reports the profile name along with the application name, event, and action

#### Scenario: Global profile selection reported
- **WHEN** the global profile is selected as fallback
- **THEN** the system reports that the global profile was used along with the application name, event, and action

### Requirement: No profile available
The system SHALL handle the case where neither an application-specific profile nor a global profile exists.

#### Scenario: No profiles configured
- **WHEN** a mouse event occurs
- **AND** no application-specific profile exists for the focused application
- **AND** no global profile exists
- **THEN** the system reports that no action is configured

#### Scenario: Window info is null
- **WHEN** a mouse event occurs with null window information
- **THEN** the system reports that no action is configured
