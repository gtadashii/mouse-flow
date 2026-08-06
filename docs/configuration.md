# Configuration Guide

MouseFlow uses a YAML configuration file to define mouse actions per application.

## Configuration File Location

The configuration file is located at:

```
~/.config/mouseflow/config.yaml
```

## Configuration Structure

The configuration file has three main sections:

1. **global** - Default actions applied when no profile matches
2. **global_gestures** - Default gesture actions
3. **profiles** - Application-specific action mappings

## Global Mappings

Global mappings define default actions that apply when no application-specific profile matches the active window.

```yaml
global:
  BTN_SIDE:
    type: keyboard
    payload: alt+left
  BTN_EXTRA:
    type: keyboard
    payload: alt+right
```

## Global Gestures

Global gestures define default gesture actions.

```yaml
global_gestures:
  UP:
    type: command
    payload: swaymsg workspace next
  DOWN:
    type: command
    payload: swaymsg workspace prev
```

## Profiles

Profiles define application-specific mappings. Each profile matches against the active window's application name.

```yaml
profiles:
  - app_name: firefox
    mappings:
      BTN_SIDE:
        type: keyboard
        payload: alt+left
      BTN_EXTRA:
        type: keyboard
        payload: alt+right
    gestures:
      LEFT:
        type: keyboard
        payload: alt+left
      RIGHT:
        type: keyboard
        payload: alt+right
```

### Profile Fields

| Field | Required | Description |
|-------|----------|-------------|
| `app_name` | Yes | Application name to match (from window title) |
| `mappings` | No | Button and wheel event mappings |
| `gestures` | No | Gesture mappings |

## Action Types

### keyboard

Simulates a keyboard shortcut.

```yaml
BTN_SIDE:
  type: keyboard
  payload: alt+left
```

**Payload format:** Modifier keys separated by `+`, followed by the key.

Supported modifiers:
- `ctrl`
- `alt`
- `shift`
- `super` (Windows/Meta key)

Examples:
- `alt+left` - Alt + Left Arrow
- `ctrl+shift+p` - Ctrl + Shift + P
- `super+t` - Super + T

### command

Executes a shell command.

```yaml
REL_HWHEEL:
  type: command
  payload: swaymsg workspace next
```

**Payload format:** Any valid shell command.

Examples:
- `swaymsg workspace next` - Switch to next workspace (Sway)
- `swaymsg workspace prev` - Switch to previous workspace (Sway)
- `notify-send "Button pressed"` - Show desktop notification

## Input Events

### Button Events

| Event | Description |
|-------|-------------|
| `BTN_SIDE` | Side button (typically thumb button) |
| `BTN_EXTRA` | Extra button (additional side button) |
| `BTN_FORWARD` | Forward button |

### Wheel Events

| Event | Description |
|-------|-------------|
| `REL_HWHEEL` | Horizontal wheel scroll |

## Gesture Events

Gestures are recognized from mouse movement patterns.

| Gesture | Description |
|---------|-------------|
| `UP` | Mouse moved up |
| `DOWN` | Mouse moved down |
| `LEFT` | Mouse moved left |
| `RIGHT` | Mouse moved right |

## Configuration Precedence

1. Application-specific profile (if active window matches)
2. Global mappings (fallback)

When a profile matches the active window, only that profile's mappings are used. Global mappings are not merged.

## Reloading Configuration

After editing the configuration file, reload it without restarting the daemon:

```bash
mouseflow config reload
```

## Validating Configuration

Check if your configuration file is valid:

```bash
mouseflow config validate
```

Validate a specific file:

```bash
mouseflow config validate /path/to/config.yaml
```

## Complete Example

```yaml
global:
  BTN_SIDE:
    type: keyboard
    payload: alt+left
  BTN_EXTRA:
    type: keyboard
    payload: alt+right

global_gestures:
  UP:
    type: command
    payload: swaymsg workspace next
  DOWN:
    type: command
    payload: swaymsg workspace prev

profiles:
  - app_name: firefox
    mappings:
      BTN_SIDE:
        type: keyboard
        payload: alt+left
      BTN_EXTRA:
        type: keyboard
        payload: alt+right
      REL_HWHEEL:
        type: command
        payload: swaymsg workspace next
    gestures:
      LEFT:
        type: keyboard
        payload: alt+left
      RIGHT:
        type: keyboard
        payload: alt+right

  - app_name: vscode
    mappings:
      BTN_SIDE:
        type: keyboard
        payload: ctrl+shift+p
      BTN_EXTRA:
        type: keyboard
        payload: ctrl+p
    gestures:
      UP:
        type: keyboard
        payload: ctrl+shift+n
      DOWN:
        type: keyboard
        payload: ctrl+shift+t
```
