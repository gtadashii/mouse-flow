## Why

After identifying the correct mouse device in Sprint 1, MouseFlow needs a reliable way to continuously receive user interactions. Without an event stream, the application cannot react to button presses, wheel movements, or future gestures. The input engine becomes the foundation for every subsequent feature.

## What Changes

- Add continuous event stream from the selected input device
- Add recognition and reporting of supported mouse events (BTN_SIDE, BTN_EXTRA, BTN_FORWARD, REL_HWHEEL)
- Add real-time display of events as they occur
- Add graceful shutdown handling to release device resources cleanly

## Capabilities

### New Capabilities
- `input-engine`: Continuous event stream from the selected mouse device with real-time event reporting

### Modified Capabilities
<!-- None - this is a new capability -->

## Impact

- **Code**: New module(s) in src/mouseflow for event streaming
- **Dependencies**: Uses existing evdev library (already installed)
- **Runtime**: Application will run continuously until interrupted (Ctrl+C)
- **Resources**: Device handle must be kept open during execution
- **Future**: Foundation for event routing, gesture recognition, and action execution
