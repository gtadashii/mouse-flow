# CLI Reference

MouseFlow provides a command-line interface for running the daemon and managing the application.

## Global Options

```bash
mouseflow --version    # Show version number
mouseflow --help       # Show help message
```

## Commands

### start

Start the MouseFlow daemon.

```bash
mouseflow start
```

The daemon runs in the foreground. Press `Ctrl+C` to stop it.

**Example output:**

```
Found device:

Logitech MX Master 3S
```

If no supported device is found:

```
No supported mouse found.
```

### status

Show the current state of the daemon.

```bash
mouseflow status
```

**Example output:**

```
Running: yes
Device: connected
Configuration: loaded
Active profile: firefox
```

**Requires:** Daemon must be running.

### devices

List all supported mouse devices detected on the system.

```bash
mouseflow devices
```

**Example output:**

```
Logitech MX Master 3S (active)
  Path: /dev/input/event5
```

If no devices are found:

```
No supported device found.
```

**Requires:** Daemon must be running.

### config

Configuration management commands.

#### config show

Show the currently loaded configuration.

```bash
mouseflow config show
```

**Example output:**

```
Profile: firefox
  BTN_SIDE: keyboard -> alt+left
  BTN_EXTRA: keyboard -> alt+right
  REL_HWHEEL: command -> swaymsg workspace next

Profile: vscode
  BTN_SIDE: keyboard -> ctrl+shift+p
  BTN_EXTRA: keyboard -> ctrl+p
```

If no configuration is loaded:

```
No configuration loaded
```

**Requires:** Daemon must be running.

#### config validate

Validate the configuration file.

```bash
mouseflow config validate
```

Validate a specific file:

```bash
mouseflow config validate /path/to/config.yaml
```

**Example output (valid):**

```
Configuration is valid
```

**Example output (invalid):**

```
Configuration is invalid
  Missing required field: profiles
  Invalid action type: unknown_type
```

**Requires:** Daemon must be running.

#### config reload

Reload the configuration file after editing.

```bash
mouseflow config reload
```

**Example output:**

```
Configuration reloaded successfully
```

**Requires:** Daemon must be running.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error |
| 130 | Interrupted (Ctrl+C) |

## Error Messages

### Daemon not running

```
Error: MouseFlow daemon is not running
Start it with: mouseflow start
```

This error appears when running any command except `start` while the daemon is not running.

### Initialization error

```
Initialization error: <description>
```

This error appears when the daemon fails to initialize, typically due to:
- No supported mouse device found
- Insufficient permissions to access input devices
- Sway IPC connection failure
