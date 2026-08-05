## Purpose

Exposes application capabilities as a public API that can be consumed by the CLI and future interfaces, providing a clean separation between external interfaces and internal component implementations.

## ADDED Requirements

### Requirement: Service layer provides device listing
The system SHALL provide a service method that returns information about all supported mouse devices connected to the system, including which device is currently active.

#### Scenario: List devices with active device
- **WHEN** service method `list_devices()` is called
- **WHEN** multiple supported devices are connected
- **THEN** service returns list of DeviceInfo objects
- **THEN** each DeviceInfo contains path, name, and is_active flag
- **THEN** exactly one device has is_active set to true

#### Scenario: List devices with no active device
- **WHEN** service method `list_devices()` is called
- **WHEN** no device is currently active
- **THEN** service returns list of DeviceInfo objects
- **THEN** all devices have is_active set to false

### Requirement: Service layer provides application status
The system SHALL provide a service method that returns the current application status including running state, device connection, configuration status, and active profile.

#### Scenario: Get status when fully operational
- **WHEN** service method `get_status()` is called
- **WHEN** daemon is running with device connected and configuration loaded
- **THEN** service returns ApplicationStatus with is_running=true
- **THEN** ApplicationStatus has device_connected=true
- **THEN** ApplicationStatus has configuration_loaded=true
- **THEN** ApplicationStatus has active_profile set to current profile name

#### Scenario: Get status with no configuration
- **WHEN** service method `get_status()` is called
- **WHEN** no configuration is loaded
- **THEN** service returns ApplicationStatus with configuration_loaded=false
- **THEN** ApplicationStatus has active_profile set to None

### Requirement: Service layer provides configuration access
The system SHALL provide a service method that returns the currently loaded configuration object.

#### Scenario: Get loaded configuration
- **WHEN** service method `get_configuration()` is called
- **WHEN** configuration is loaded
- **THEN** service returns Configuration domain object
- **THEN** Configuration contains all loaded profiles

#### Scenario: Get configuration when none loaded
- **WHEN** service method `get_configuration()` is called
- **WHEN** no configuration is loaded
- **THEN** service raises appropriate exception or returns None

### Requirement: Service layer provides configuration validation
The system SHALL provide a service method that validates a configuration file without loading it into the running application.

#### Scenario: Validate valid configuration
- **WHEN** service method `validate_configuration(path)` is called
- **WHEN** configuration file is valid
- **THEN** service returns ValidationResult with is_valid=true
- **THEN** ValidationResult has empty errors tuple

#### Scenario: Validate invalid configuration
- **WHEN** service method `validate_configuration(path)` is called
- **WHEN** configuration file has errors
- **THEN** service returns ValidationResult with is_valid=false
- **THEN** ValidationResult contains tuple of error messages

#### Scenario: Validate non-existent file
- **WHEN** service method `validate_configuration(path)` is called
- **WHEN** file does not exist
- **THEN** service returns ValidationResult with is_valid=false
- **THEN** ValidationResult contains error message about missing file

### Requirement: Service layer provides configuration reload
The system SHALL provide a service method that reloads the configuration from disk and updates the running application state.

#### Scenario: Successful configuration reload
- **WHEN** service method `reload_configuration()` is called
- **WHEN** configuration file is valid
- **THEN** service parses new configuration
- **THEN** service updates application state with new configuration
- **THEN** service returns ReloadResult with success=true

#### Scenario: Configuration reload fails
- **WHEN** service method `reload_configuration()` is called
- **WHEN** configuration file is invalid
- **THEN** service does not update application state
- **THEN** service returns ReloadResult with success=false
- **THEN** ReloadResult contains error message

### Requirement: Service layer wraps existing components
The Service Layer SHALL delegate to existing components (DeviceDiscovery, ConfigurationParser, etc.) and SHALL NOT duplicate business logic.

#### Scenario: Service delegates to discovery
- **WHEN** service method `list_devices()` is called
- **THEN** service calls DeviceDiscovery to find devices
- **THEN** service converts results to DeviceInfo objects
- **THEN** service does not implement device discovery logic

#### Scenario: Service delegates to parser
- **WHEN** service method `reload_configuration()` is called
- **THEN** service calls ConfigurationParser to parse file
- **THEN** service updates daemon state with parsed configuration
- **THEN** service does not implement parsing logic

### Requirement: Service layer returns immutable objects
All service methods SHALL return frozen dataclass objects (domain objects or operational objects) to ensure immutability and type safety.

#### Scenario: Service returns DeviceInfo
- **WHEN** service method returns DeviceInfo
- **THEN** DeviceInfo is a frozen dataclass
- **THEN** DeviceInfo cannot be modified after creation

#### Scenario: Service returns ApplicationStatus
- **WHEN** service method returns ApplicationStatus
- **THEN** ApplicationStatus is a frozen dataclass
- **THEN** ApplicationStatus cannot be modified after creation

### Requirement: Service layer is testable in isolation
The Service Layer SHALL be testable without requiring actual hardware, IPC, or running daemon by accepting component dependencies via constructor injection.

#### Scenario: Test service with mocked components
- **WHEN** Service Layer is instantiated with mock components
- **WHEN** service methods are called
- **THEN** service delegates to mock components
- **THEN** tests can verify service behavior without infrastructure
