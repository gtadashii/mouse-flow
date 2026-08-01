## Purpose

Automatically locates and identifies supported mouse devices connected to the system, enabling MouseFlow to select the correct device without manual configuration.

## Requirements

### Requirement: Device enumeration
The system SHALL enumerate all available input devices on the system.

#### Scenario: Multiple devices present
- **WHEN** the system has multiple input devices connected
- **THEN** the system inspects each device to determine if it is a supported mouse

#### Scenario: No devices present
- **WHEN** no input devices are available
- **THEN** the system reports that no supported device was found

### Requirement: Device identification
The system SHALL determine whether a device is a supported mouse based on its capabilities.

#### Scenario: Supported mouse detected
- **WHEN** a device with mouse capabilities and supported button mappings is found
- **THEN** the device is marked as supported

#### Scenario: Unsupported device detected
- **WHEN** a device lacks required mouse capabilities or button mappings
- **THEN** the device is ignored

### Requirement: Automatic device selection
The system SHALL automatically select the most appropriate supported device when multiple are available.

#### Scenario: Single supported device
- **WHEN** exactly one supported mouse is detected
- **THEN** that device is selected

#### Scenario: Multiple supported devices
- **WHEN** multiple supported mice are detected
- **THEN** the system selects one device deterministically

### Requirement: User feedback on device selection
The system SHALL report which device was selected to the user.

#### Scenario: Device found and selected
- **WHEN** a supported device is successfully selected
- **THEN** the system displays the device name (e.g., "Found device: Logitech MX Master 3S")

#### Scenario: No device found
- **WHEN** no supported device is available
- **THEN** the system displays a clear error message (e.g., "No supported mouse found.")

### Requirement: Graceful startup
The system SHALL start quickly and exit gracefully when no device is found.

#### Scenario: Successful startup
- **WHEN** a supported device is found
- **THEN** the application reports the device and remains ready for subsequent operations

#### Scenario: Failed startup
- **WHEN** no supported device is found
- **THEN** the application exits with a non-zero status code
