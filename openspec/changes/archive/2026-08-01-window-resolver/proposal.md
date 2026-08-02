## Why

MouseFlow needs to execute different actions depending on the active application. Without knowing which window currently has focus, the application cannot provide application-specific behavior. This capability is foundational for the per-application mouse actions that define MouseFlow's core functionality.

## What Changes

- Add ability to determine which window currently has focus
- Add extraction of application identifier from focused window
- Add extraction of window title from focused window
- Add presentation of resolved window information in human-readable format

## Capabilities

### New Capabilities

- `window-resolver`: Identifies the currently focused window and extracts application name and window title

### Modified Capabilities

<!-- None - this is a new capability -->

## Impact

- **Dependencies**: May require compositor-specific APIs (Sway IPC, X11 Xlib, etc.)
- **Code**: New module in src/mouseflow/ for window resolution
- **Runtime**: Application will query window manager state
- **Future**: Foundation for combining mouse events with window context in Sprint 4
