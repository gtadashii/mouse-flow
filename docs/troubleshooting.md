# Troubleshooting

Common issues and their solutions.

## "No supported mouse found"

This is usually a **permission issue**. MouseFlow needs access to `/dev/input` devices.

### Check available devices

```bash
ls -la /dev/input/event*
```

If you see `crw-rw----` with group `input`, you need to add your user to that group.

### Fix permissions

1. Add your user to the `input` group:

   ```bash
   sudo usermod -aG input $USER
   ```

2. **Log out and log back in** (or restart your system) for the group change to take effect.

3. Verify you are in the group:

   ```bash
   groups
   ```

   You should see `input` in the list.

### Test without logging out

If you want to test immediately without logging out, run with sudo:

```bash
sudo mouseflow start
```

### List all input devices

To see what devices are available:

```bash
python -c "from evdev import list_devices, InputDevice; [print(f'{d.path}: {d.name}') for d in [InputDevice(p) for p in list_devices()]]"
```

### Check device capabilities

To see if your mouse has the required buttons:

```bash
python -c "from evdev import InputDevice; d = InputDevice('/dev/input/eventX'); print(d.capabilities(verbose=True))"
```

Replace `eventX` with your device path (e.g., `event0`, `event1`).

## Window information not displayed

MouseFlow uses Sway's IPC protocol to identify the active window. If window information is not displayed:

### Verify Sway is running

```bash
swaymsg -t get_version
```

This should return version information if Sway is running.

### Check Sway socket

The Sway IPC socket is typically at `$SWAYSOCK` or `~/.sway-ipc.*.sock`. Verify it exists:

```bash
ls -la $SWAYSOCK
```

### Test Sway IPC manually

```bash
swaymsg -t get_tree
```

This should return a JSON tree of all windows.

### Not using Sway?

If you are not using Sway, window resolution is not yet supported. Future versions will add support for other Wayland compositors.

## Installation Issues

### Permission denied during installation

If you get a permission error when installing with pip:

```bash
pip install mouseflow
```

Use the `--user` flag:

```bash
pip install --user mouseflow
```

Or use `uv tool install` which handles this automatically:

```bash
uv tool install mouseflow
```

### Command not found after installation

If `mouseflow` is not found after installation, ensure the installation binary directory is in your PATH.

For pip with `--user`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

For uv tool:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add the export to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.) to make it permanent.

### Dependency conflicts

If you encounter dependency conflicts during installation, try installing in an isolated environment:

```bash
python -m venv /tmp/mouseflow-env
/tmp/mouseflow-env/bin/pip install mouseflow
/tmp/mouseflow-env/bin/mouseflow start
```

Or use `uv tool install` which creates an isolated environment automatically:

```bash
uv tool install mouseflow
```

## Configuration Issues

### Configuration file not found

MouseFlow looks for the configuration file at `~/.config/mouseflow/config.yaml`. If it does not exist, MouseFlow starts with no configuration.

Create the directory and file:

```bash
mkdir -p ~/.config/mouseflow
touch ~/.config/mouseflow/config.yaml
```

See the [Configuration Guide](configuration.md) for the file format.

### Invalid configuration

Validate your configuration file:

```bash
mouseflow config validate
```

Common issues:
- Missing required fields
- Invalid action types (must be `keyboard` or `command`)
- Invalid payload format

### Configuration not reloading

After editing the configuration file, reload it:

```bash
mouseflow config reload
```

If reload fails, check that the daemon is running:

```bash
mouseflow status
```

## Service Issues

### Service fails to start

Check the service status:

```bash
systemctl --user status mouseflow
```

View detailed logs:

```bash
journalctl --user -u mouseflow -f
```

Common causes:
- MouseFlow not installed in `~/.local/bin/`
- Insufficient permissions (see "No supported mouse found" above)
- Sway not running

### Service starts but immediately stops

Check the logs for errors:

```bash
journalctl --user -u mouseflow --since "5 minutes ago"
```

The service has automatic restart configured (`Restart=on-failure`). If it keeps restarting, there is likely a persistent error.

## Getting Help

If you encounter an issue not covered here:

1. Check the [GitHub Issues](https://github.com/gtadashii/mouse-flow/issues) for known problems
2. Open a new issue with:
   - MouseFlow version (`mouseflow --version`)
   - Linux distribution and version
   - Wayland compositor and version
   - Mouse model
   - Relevant log output
