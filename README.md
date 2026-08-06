# MouseFlow

Per-application mouse actions for Wayland compositors.

## Installation

### From PyPI

Using pip:

```bash
pip install mouseflow
```

Using uv:

```bash
uv tool install mouseflow
```

### From Source

```bash
git clone https://github.com/gtadashii/mouse-flow.git
cd mouse-flow
pip install .
```

Or with uv:

```bash
git clone https://github.com/gtadashii/mouse-flow.git
cd mouse-flow
uv build
uv tool install dist/mouseflow-*.whl
```

## Usage

### Starting the Daemon

```bash
mouseflow start
```

This starts the MouseFlow daemon in the foreground. If a supported mouse is detected, you'll see:

```
Found device:

Logitech MX Master 3S
```

Press `Ctrl+C` to stop the daemon.

### CLI Commands

```bash
mouseflow start            # Start the daemon
mouseflow status           # Show application status
mouseflow devices          # List available mouse devices
mouseflow config show      # Show loaded configuration
mouseflow config validate  # Validate configuration file
mouseflow config reload    # Reload configuration
```

**Note:** All commands except `start` require the daemon to be running.

#### Status

```bash
$ mouseflow status
Running: yes
Device: connected
Configuration: loaded
Active profile: firefox
```

#### Devices

```bash
$ mouseflow devices
Logitech MX Master 3S (active)
  Path: /dev/input/event5
```

#### Configuration

```bash
mouseflow config show
mouseflow config validate
mouseflow config validate /path/to/config.yaml
mouseflow config reload
```

### Running as a Background Service

MouseFlow can run as a systemd user service, starting automatically with your desktop session.

1. Copy the service file to your user systemd directory:

   ```bash
   mkdir -p ~/.config/systemd/user/
   cp packaging/mouseflow.service ~/.config/systemd/user/
   ```

2. Enable and start the service:

   ```bash
   systemctl --user enable mouseflow
   systemctl --user start mouseflow
   ```

3. Check the service status:

   ```bash
   systemctl --user status mouseflow
   ```

4. View logs:

   ```bash
   journalctl --user -u mouseflow -f
   ```

To stop the service:

```bash
systemctl --user stop mouseflow
```

To disable automatic startup:

```bash
systemctl --user disable mouseflow
```

## Configuration

MouseFlow uses a YAML configuration file located at `~/.config/mouseflow/config.yaml`.

Example configuration:

```yaml
global:
  BTN_SIDE:
    type: keyboard
    payload: alt+left
  BTN_EXTRA:
    type: keyboard
    payload: alt+right

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
```

See [Configuration Guide](docs/configuration.md) for full details.

## Requirements

- **Linux** with Wayland compositor (Sway recommended)
- **Sway IPC**: MouseFlow uses Sway's IPC protocol to identify the active window
- **Input device permissions**: See [Troubleshooting](docs/troubleshooting.md)

## Supported Devices

MouseFlow automatically detects mice with:
- Left and right buttons
- At least one side button (BTN_SIDE or BTN_EXTRA)
- Relative X/Y axes

Compatible devices include:
- Logitech MX Master series (3, 3S, etc.)
- Other mice with side buttons

## Supported Events

- **BTN_SIDE** - Side button (typically thumb button)
- **BTN_EXTRA** - Extra button (additional side button)
- **BTN_FORWARD** - Forward button
- **REL_HWHEEL** - Horizontal wheel scroll

More events will be supported in future versions.

## Documentation

- [Configuration Guide](docs/configuration.md)
- [CLI Reference](docs/cli-reference.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Architecture](docs/architecture.md)

## Development

### Setup

```bash
git clone https://github.com/gtadashii/mouse-flow.git
cd mouse-flow
uv sync --extra dev
pre-commit install
```

### Quality Checks

```bash
make check       # Run all checks
make format      # Check formatting
make lint        # Run linter
make typecheck   # Type checking
make test        # Run tests
```

## License

MIT License. See [LICENSE](LICENSE) for details.
