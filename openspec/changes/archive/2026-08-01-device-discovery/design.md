## Context

The project currently has a basic Python structure with quality tools configured (ruff, mypy, pytest, pre-commit, CI). No application logic exists yet. This sprint introduces the first functional capability: device discovery using evdev to access Linux input devices.

Constraints:
- Python 3.13+
- evdev library for input device access
- Must work on Linux/Wayland (primary target: Sway)
- Requires access to /dev/input devices

## Goals / Non-Goals

**Goals:**
- Discover input devices using evdev
- Identify supported mice based on device capabilities
- Select the appropriate device automatically
- Report the selected device to the user
- Handle missing/unsupported devices gracefully

**Non-Goals:**
- Reading input events (Sprint 2)
- Window/application detection (Sprint 3)
- Configuration loading (Sprint 6)
- Action execution (Sprint 7)
- Background service mode (Sprint 11)

## Decisions

### Decision 1: Use evdev library for device access

**Choice:** python-evdev

**Rationale:** evdev is the standard Python interface to Linux input devices. It provides direct access to /dev/input/event* devices and exposes device capabilities, names, and properties. It's well-maintained and widely used in the Linux Python ecosystem.

**Alternatives considered:**
- Direct /dev/input access: More complex, requires handling raw input_event structs
- libinput: Higher-level but less control over device enumeration

### Decision 2: Identify supported devices by capability flags

**Choice:** Check device capabilities (BTN_LEFT, BTN_RIGHT, BTN_SIDE, BTN_EXTRA, REL_X, REL_Y)

**Rationale:** Device names can vary by vendor and model. Capability flags are more reliable for identifying mice with the required buttons. A supported mouse must have basic mouse buttons plus at least one side button (BTN_SIDE or BTN_EXTRA).

**Alternatives considered:**
- Device name matching: Fragile, vendor-specific naming conventions
- VID/PID matching: Requires maintaining a device database

### Decision 3: Use a simple device registry for supported devices

**Choice:** Define supported device criteria as capability requirements

**Rationale:** Instead of maintaining a list of specific device models, define the minimum capability requirements. This allows any mouse meeting the criteria to work without code changes.

**Alternatives considered:**
- Hardcoded device list: Inflexible, requires updates for new devices
- Configuration file: Over-engineering for initial implementation

### Decision 4: Single device selection strategy

**Choice:** Select the first supported device found (deterministic order by device path)

**Rationale:** Most users have one primary mouse. When multiple are present, selecting the first by device path (/dev/input/eventX) provides deterministic behavior. Future sprints can add device selection configuration.

**Alternatives considered:**
- User selection prompt: Adds complexity, not needed for single-device use case
- Priority-based selection: Over-engineering for initial implementation

### Decision 5: Module structure

**Choice:** Create a `discovery` module with a `find_supported_device()` function

**Rationale:** Single responsibility, testable, pure function that returns an Optional device. Easy to mock in tests. Follows project principle of composition over inheritance.

**Alternatives considered:**
- DeviceManager class: Unnecessary abstraction for single-device scenario
- Generator-based discovery: Over-engineering for initial implementation

## Risks / Trade-offs

**Risk:** Permission issues accessing /dev/input devices
→ **Mitigation:** Document required permissions (input group or udev rules). Consider adding a diagnostic command in Sprint 12.

**Risk:** Device capability detection may not work for all mice
→ **Mitigation:** Start with common capability requirements. Can be refined based on user feedback.

**Risk:** evdev library adds a dependency
→ **Mitigation:** evdev is essential for Linux input device access. No standard library alternative exists.

**Trade-off:** First-device selection may not always be correct
→ **Acceptance:** Acceptable for initial implementation. Device selection configuration can be added in future sprints.

**Trade-off:** Capability-based detection may miss some devices
→ **Acceptance:** Conservative approach avoids false positives. Can expand criteria based on real-world testing.
