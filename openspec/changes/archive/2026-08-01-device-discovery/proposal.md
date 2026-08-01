## Why

Linux systems expose multiple input devices simultaneously (keyboards, touchpads, webcams, virtual devices, multiple mice). MouseFlow needs to automatically identify the correct supported mouse without requiring manual configuration, as manual device path configuration would significantly reduce usability.

## What Changes

- Add ability to discover connected input devices using evdev
- Add device identification logic to determine if a device is supported
- Add automatic selection of the most appropriate supported device
- Add user feedback reporting the selected device
- Add graceful failure handling when no supported device is found

## Capabilities

### New Capabilities
- `device-discovery`: Automatically locate and identify supported mouse devices connected to the system using evdev

### Modified Capabilities
<!-- None - this is a new capability -->

## Impact

- **Dependencies**: evdev library for input device access
- **Code**: New module(s) in src/mouseflow for device discovery
- **Permissions**: Requires access to /dev/input devices (may need uinput group or similar)
- **Future**: Foundation for subsequent sprints (input engine, event handling)
