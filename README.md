# Mouse Flow

Per-application mouse actions for Wayland compositors.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gtadashii/mouse-flow.git
   cd mouse-flow
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

3. Install pre-commit hooks (for development):
   ```bash
   .venv/bin/pre-commit install
   ```

## Usage

MouseFlow provides a command-line interface for running the daemon and managing the application.

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

MouseFlow provides several commands for inspecting and managing the running daemon:

```bash
mouseflow status          # Show application status
mouseflow devices         # List available mouse devices
mouseflow config show     # Show loaded configuration
mouseflow config validate # Validate configuration file
mouseflow config reload   # Reload configuration
```

**Note:** All commands except `start` require the daemon to be running.

#### Status

Shows the current state of the daemon:

```bash
$ mouseflow status
Running: yes
Device: connected
Configuration: loaded
Active profile: firefox
```

#### Devices

Lists all supported mouse devices:

```bash
$ mouseflow devices
Logitech MX Master 3S (active)
  Path: /dev/input/event5
```

#### Configuration

View and manage configuration:

```bash
# Show loaded configuration
mouseflow config show

# Validate configuration file
mouseflow config validate
mouseflow config validate /path/to/config.yaml

# Reload configuration after editing
mouseflow config reload
```

### Running as a Background Service

MouseFlow can run as a systemd user service, starting automatically with your desktop session.

1. Install the package:
   ```bash
   uv pip install .
   ```

2. Copy the service file to your user systemd directory:
   ```bash
   mkdir -p ~/.config/systemd/user/
   cp packaging/mouseflow.service ~/.config/systemd/user/
   ```

3. Enable and start the service:
   ```bash
   systemctl --user enable mouseflow
   systemctl --user start mouseflow
   ```

4. Check the service status:
   ```bash
   systemctl --user status mouseflow
   ```

5. View logs:
   ```bash
   journalctl --user -u mouseflow -f
   ```

6. Use CLI commands to inspect the running daemon:
   ```bash
   mouseflow status
   mouseflow devices
   mouseflow config show
   ```

To stop the service:
```bash
systemctl --user stop mouseflow
```

To disable automatic startup:
```bash
systemctl --user disable mouseflow
```

To reload configuration after editing:
```bash
mouseflow config reload
```

If no supported device is found:

```
No supported mouse found.
```

### Requirements

- **Linux** with Wayland compositor (Sway recommended)
- **Sway IPC**: MouseFlow uses Sway's IPC protocol to identify the active window. Ensure Sway is running.
- **Input device permissions**: See [Troubleshooting](#troubleshooting) below.

### Supported Devices

MouseFlow automatically detects mice with:
- Left and right buttons
- At least one side button (BTN_SIDE or BTN_EXTRA)
- Relative X/Y axes

Compatible devices include:
- Logitech MX Master series (3, 3S, etc.)
- Other mice with side buttons

### Supported Events

MouseFlow currently recognizes these mouse events:
- **BTN_SIDE** - Side button (typically thumb button)
- **BTN_EXTRA** - Extra button (additional side button)
- **BTN_FORWARD** - Forward button
- **REL_HWHEEL** - Horizontal wheel scroll

More events will be supported in future versions.

### Troubleshooting

#### "No supported mouse found" but you have a compatible mouse

This is usually a **permission issue**. MouseFlow needs access to `/dev/input` devices.

**Check available devices:**

```bash
ls -la /dev/input/event*
```

If you see `crw-rw----` with group `input`, you need to add your user to that group.

**Fix permissions:**

1. Add your user to the `input` group:
   ```bash
   sudo usermod -aG input $USER
   ```

2. **Log out and log back in** (or restart your system) for the group change to take effect.

3. Verify you're in the group:
   ```bash
   groups
   ```
   You should see `input` in the list.

**Test without logging out:**

If you want to test immediately without logging out, run with sudo:

```bash
sudo .venv/bin/python -m mouseflow
```

Or use the full path to `uv`:

```bash
sudo $HOME/.local/bin/uv run mouseflow
```

Note: `sudo uv run mouseflow` won't work because `uv` is in your user's PATH, not root's.

**List all input devices:**

To see what devices are available:

```bash
.venv/bin/python -c "from evdev import list_devices, InputDevice; [print(f'{d.path}: {d.name}') for d in [InputDevice(p) for p in list_devices()]]"
```

**Check device capabilities:**

To see if your mouse has the required buttons:

```bash
.venv/bin/python -c "from evdev import InputDevice; d = InputDevice('/dev/input/eventX'); print(d.capabilities(verbose=True))"
```

Replace `eventX` with your device path (e.g., `event0`, `event1`).

#### Window information not displayed

MouseFlow uses Sway's IPC protocol to identify the active window. If window information is not displayed:

1. **Verify Sway is running:**
   ```bash
   swaymsg -t get_version
   ```
   This should return version information if Sway is running.

2. **Check Sway socket:**
   The Sway IPC socket is typically at `$SWAYSOCK` or `~/.sway-ipc.*.sock`. Verify it exists:
   ```bash
   ls -la $SWAYSOCK
   ```

3. **Test Sway IPC manually:**
   ```bash
   swaymsg -t get_tree
   ```
   This should return a JSON tree of all windows.

If you're not using Sway, window resolution is not yet supported. Future versions will add support for other Wayland compositors.

## Development

### Setup

```bash
uv sync --extra dev
pre-commit install
```

### Quality Checks

Run all quality checks:

```bash
make check
```

Or run individually:

```bash
make format    # Check formatting
make lint      # Run linter
make typecheck # Type checking
make test      # Run tests
```

**Note:** The Makefile uses `.venv/bin/` directly, so you don't need `uv` in your PATH after initial setup.

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit. They check:
- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Tests (pytest)

To run manually:

```bash
pre-commit run --all-files
```
