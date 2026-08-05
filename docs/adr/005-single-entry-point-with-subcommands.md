# ADR-005: Single Entry Point with Subcommands

## Status

Proposed

## Context

Sprint 12 introduces a Command Line Interface (CLI) for MouseFlow. The CLI needs to support multiple commands:
- `status` - Show application status
- `devices` - List available devices
- `show` - Show loaded configuration
- `validate` - Validate configuration file
- `reload` - Reload configuration

Additionally, the daemon needs to be started somehow. Currently, the daemon is started via `uv run mouseflow` which directly executes `__main__.py`.

We need to decide how to structure the entry points for both the daemon and CLI commands.

## Decision

Use a **single entry point** (`mouseflow`) with **subcommands** for all operations.

### Command Structure

```bash
# Daemon commands
mouseflow start              # Start daemon (foreground)
mouseflow start --daemon     # Start daemon (background, future)

# CLI commands (require running daemon)
mouseflow status             # Show application status
mouseflow devices            # List available devices
mouseflow config show        # Show loaded configuration
mouseflow config validate    # Validate configuration file
mouseflow config reload      # Reload configuration

# Utility commands
mouseflow --help             # Show help
mouseflow --version          # Show version
```

### Entry Point

Single entry point in `pyproject.toml`:

```toml
[project.scripts]
mouseflow = "mouseflow.cli:main"
```

### CLI Structure

```python
# src/mouseflow/cli.py
import argparse
import sys

def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    return args.func(args)

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='mouseflow',
        description='MouseFlow - Per-application mouse actions for Wayland'
    )
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    
    subparsers = parser.add_subparsers(title='commands')
    
    # start command
    start_parser = subparsers.add_parser('start', help='Start MouseFlow daemon')
    start_parser.set_defaults(func=cmd_start)
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show application status')
    status_parser.set_defaults(func=cmd_status)
    
    # devices command
    devices_parser = subparsers.add_parser('devices', help='List available devices')
    devices_parser.set_defaults(func=cmd_devices)
    
    # config command group
    config_parser = subparsers.add_parser('config', help='Configuration commands')
    config_subparsers = config_parser.add_subparsers()
    
    config_show = config_subparsers.add_parser('show', help='Show loaded configuration')
    config_show.set_defaults(func=cmd_config_show)
    
    config_validate = config_subparsers.add_parser('validate', help='Validate configuration')
    config_validate.set_defaults(func=cmd_config_validate)
    
    config_reload = config_subparsers.add_parser('reload', help='Reload configuration')
    config_reload.set_defaults(func=cmd_config_reload)
    
    return parser

def cmd_start(args: argparse.Namespace) -> int:
    from mouseflow.daemon import Daemon
    daemon = Daemon()
    daemon.run()
    return 0

def cmd_status(args: argparse.Namespace) -> int:
    from mouseflow.ipc_client import IPCClient
    client = IPCClient()
    response = client.send_command('status')
    # Format and display response
    return 0

# ... other command functions
```

## Alternatives Considered

### 1. Separate Entry Points

Two separate entry points: `mouseflow` (daemon) and `mouseflow-cli` (CLI).

```bash
# Daemon
mouseflow                    # Start daemon

# CLI (separate command)
mouseflow-cli status
mouseflow-cli devices
mouseflow-cli config show
```

**Entry points:**
```toml
[project.scripts]
mouseflow = "mouseflow.daemon:main"
mouseflow-cli = "mouseflow.cli:main"
```

**Pros:**
- Clear separation between daemon and CLI
- Daemon entry point is simple (just runs daemon)
- CLI can be packaged/installed separately

**Cons:**
- Two commands to remember
- Less intuitive for users
- Harder to document
- Doesn't follow common CLI patterns (git, docker, etc.)
- systemd service needs to call `mouseflow` (daemon entry point)

**Why not chosen:** Single entry point is more intuitive and follows common CLI tool patterns.

### 2. Environment Variable Mode

Single binary that behaves differently based on environment variable.

```bash
MOUSEFLOW_MODE=daemon mouseflow      # Start daemon
MOUSEFLOW_MODE=cli mouseflow status  # CLI command
```

**Pros:**
- Single binary
- Can detect mode automatically

**Cons:**
- Non-standard, confusing
- Hard to discover
- Poor user experience
- Doesn't follow Unix conventions

**Why not chosen:** Terrible UX. Non-standard and confusing.

### 3. Automatic Mode Detection

Single binary that automatically detects if it should run as daemon or CLI.

```bash
mouseflow              # If no args, start daemon
mouseflow status       # If args, run CLI command
```

**Pros:**
- Simple for common case
- No subcommand needed for daemon

**Cons:**
- Ambiguous (what if I want daemon with args?)
- Hard to add daemon-specific options
- Inconsistent behavior
- Confusing for users

**Why not chosen:** Ambiguous and limits future extensibility. Explicit `start` command is clearer.

### 4. Separate Binary Names

Different binary names for different functions.

```bash
mouseflowd             # Daemon (d for daemon)
mouseflow-status       # Status command
mouseflow-devices      # Devices command
```

**Pros:**
- Very explicit
- Each command is separate

**Cons:**
- Many binaries to install
- Hard to maintain
- Doesn't scale (many commands = many binaries)
- Non-standard pattern

**Why not chosen:** Doesn't scale, hard to maintain, non-standard.

## Trade-offs

### Pros

1. **Intuitive:** Single command, familiar pattern (git, docker, kubectl)
2. **Discoverable:** `mouseflow --help` shows all commands
3. **Consistent:** All commands follow same pattern
4. **Scalable:** Easy to add new commands
5. **Simple:** One entry point to maintain
6. **Standard:** Follows common CLI tool conventions
7. **Documentable:** Single command to document

### Cons

1. **Complexity:** CLI parser needs to handle both daemon and CLI commands
2. **Mode Switching:** `start` command needs to run daemon, others need IPC
3. **Dependency Management:** CLI commands need IPC client, daemon doesn't
4. **Testing:** Need to test both daemon startup and CLI commands

## Consequences

### Positive

- Users learn one command (`mouseflow`) and discover subcommands
- Consistent with popular CLI tools (git, docker, etc.)
- Easy to add new commands (just add subparser)
- Single entry point simplifies packaging and distribution
- `--help` provides discoverability
- systemd service uses `mouseflow start`

### Negative

- CLI module needs to handle both daemon startup and IPC communication
- Need to distinguish between "local" commands (start) and "remote" commands (status, devices)
- Slightly more complex CLI structure

### Neutral

- Entry point is simple (calls `cli.main()`)
- Daemon startup is just another command (`start`)
- Can refactor CLI into modules if it grows

## Implementation

### Module Structure

```
src/mouseflow/
├── cli.py               # Main CLI entry point and parser
├── cli_commands.py      # Command implementations (or split into modules)
```

Or split into command modules:

```
src/mouseflow/
├── cli/
│   ├── __init__.py      # main() and create_parser()
│   ├── start.py         # cmd_start
│   ├── status.py        # cmd_status
│   ├── devices.py       # cmd_devices
│   └── config.py        # cmd_config_*
```

**Recommendation:** Start with single `cli.py` module. Split if it grows beyond ~400 lines.

### Command Routing

```python
def cmd_start(args: argparse.Namespace) -> int:
    """Start MouseFlow daemon."""
    from mouseflow.daemon import Daemon
    daemon = Daemon()
    daemon.run()
    return 0

def cmd_status(args: argparse.Namespace) -> int:
    """Show application status."""
    from mouseflow.ipc_client import IPCClient
    try:
        client = IPCClient()
        response = client.send_command('status')
        format_status(response['data'])
        return 0
    except ConnectionError:
        print("Error: MouseFlow daemon is not running", file=sys.stderr)
        print("Start it with: mouseflow start", file=sys.stderr)
        return 1

def cmd_devices(args: argparse.Namespace) -> int:
    """List available devices."""
    from mouseflow.ipc_client import IPCClient
    try:
        client = IPCClient()
        response = client.send_command('devices')
        format_devices(response['data'])
        return 0
    except ConnectionError:
        print("Error: MouseFlow daemon is not running", file=sys.stderr)
        return 1
```

### systemd Integration

Service file uses `mouseflow start`:

```ini
[Service]
ExecStart=/usr/bin/mouseflow start
```

### Help Output

```
$ mouseflow --help
usage: mouseflow [-h] [--version] {start,status,devices,config} ...

MouseFlow - Per-application mouse actions for Wayland

options:
  -h, --help            show this help message and exit
  --version             show version

commands:
  {start,status,devices,config}
    start               Start MouseFlow daemon
    status              Show application status
    devices             List available devices
    config              Configuration commands
```

## Related Decisions

- **ADR-003:** Unix socket IPC used by CLI commands (status, devices, config)
- **ADR-004:** Service layer provides API that CLI commands invoke via IPC

## References

- [argparse Documentation](https://docs.python.org/3/library/argparse.html)
- [Click vs Argparse](https://click.palletsprojects.com/en/8.x/why/)
- [Command-line interface design guidelines](https://clig.dev/)
- Project AGENTS.md: "Prefer the standard library unless there is a compelling reason not to"
