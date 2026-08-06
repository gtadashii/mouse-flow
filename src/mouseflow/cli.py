from __future__ import annotations

import argparse
import sys
from typing import Any

from mouseflow.daemon import Daemon, DaemonError, DaemonInitializationError
from mouseflow.ipc import IPCClient, IPCConnectionError

VERSION = "1.0.1"


def main() -> int:
    parser = _create_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mouseflow",
        description="MouseFlow - Per-application mouse actions for Wayland",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )

    subparsers = parser.add_subparsers(title="commands")

    start_parser = subparsers.add_parser("start", help="Start MouseFlow daemon")
    start_parser.set_defaults(func=_cmd_start)

    status_parser = subparsers.add_parser("status", help="Show application status")
    status_parser.set_defaults(func=_cmd_status)

    devices_parser = subparsers.add_parser("devices", help="List available devices")
    devices_parser.set_defaults(func=_cmd_devices)

    config_parser = subparsers.add_parser("config", help="Configuration commands")
    config_subparsers = config_parser.add_subparsers()

    config_show = config_subparsers.add_parser("show", help="Show loaded configuration")
    config_show.set_defaults(func=_cmd_config_show)

    config_validate = config_subparsers.add_parser(
        "validate",
        help="Validate configuration file",
    )
    config_validate.add_argument(
        "path",
        nargs="?",
        help="Path to configuration file (default: ~/.config/mouseflow/config.yaml)",
    )
    config_validate.set_defaults(func=_cmd_config_validate)

    config_reload = config_subparsers.add_parser(
        "reload",
        help="Reload configuration",
    )
    config_reload.set_defaults(func=_cmd_config_reload)

    return parser


def _cmd_start(_args: argparse.Namespace) -> int:
    try:
        daemon = Daemon()
        daemon.run()
        return 0
    except DaemonInitializationError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        return 1
    except DaemonError as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


def _cmd_status(_args: argparse.Namespace) -> int:
    try:
        client = IPCClient()
        response = client.send_command("status")
    except IPCConnectionError:
        print("Error: MouseFlow daemon is not running", file=sys.stderr)
        print("Start it with: mouseflow start", file=sys.stderr)
        return 1

    if response["status"] != "ok":
        print(f"Error: {response['message']}", file=sys.stderr)
        return 1

    data = response["data"]
    _format_status(data)
    return 0


def _format_status(data: dict[str, Any]) -> None:
    running = "yes" if data["is_running"] else "no"
    print(f"Running: {running}")

    device = "connected" if data["device_connected"] else "disconnected"
    print(f"Device: {device}")

    config = "loaded" if data["configuration_loaded"] else "not loaded"
    print(f"Configuration: {config}")

    profile = data.get("active_profile") or "none"
    print(f"Active profile: {profile}")


def _cmd_devices(_args: argparse.Namespace) -> int:
    try:
        client = IPCClient()
        response = client.send_command("devices")
    except IPCConnectionError:
        print("Error: MouseFlow daemon is not running", file=sys.stderr)
        print("Start it with: mouseflow start", file=sys.stderr)
        return 1

    if response["status"] != "ok":
        print(f"Error: {response['message']}", file=sys.stderr)
        return 1

    devices = response["data"]
    if not devices:
        print("No supported devices found")
        return 0

    _format_devices(devices)
    return 0


def _format_devices(devices: list[dict[str, Any]]) -> None:
    for device in devices:
        marker = " (active)" if device["is_active"] else ""
        print(f"{device['name']}{marker}")
        print(f"  Path: {device['path']}")


def _cmd_config_show(_args: argparse.Namespace) -> int:
    try:
        client = IPCClient()
        response = client.send_command("config_show")
    except IPCConnectionError:
        print("Error: MouseFlow daemon is not running", file=sys.stderr)
        print("Start it with: mouseflow start", file=sys.stderr)
        return 1

    if response["status"] != "ok":
        print(f"Error: {response['message']}", file=sys.stderr)
        return 1

    config = response["data"]
    if config is None:
        print("No configuration loaded")
        return 0

    _format_configuration(config)
    return 0


def _format_configuration(config: dict[str, Any]) -> None:
    profiles = config.get("profiles", [])
    if not profiles:
        print("No profiles configured")
        return

    for profile in profiles:
        app_name = profile["app_name"]
        print(f"Profile: {app_name}")
        mappings = profile.get("mappings", {})
        if not mappings:
            print("  (no mappings)")
        else:
            for input_id, action in mappings.items():
                action_type = action["type"]
                payload = action["payload"]
                print(f"  {input_id}: {action_type} -> {payload}")
        print()


def _cmd_config_validate(args: argparse.Namespace) -> int:
    path = getattr(args, "path", None)
    cmd_args = {"path": path} if path else {}

    try:
        client = IPCClient()
        response = client.send_command("config_validate", cmd_args)
    except IPCConnectionError:
        print("Error: MouseFlow daemon is not running", file=sys.stderr)
        print("Start it with: mouseflow start", file=sys.stderr)
        return 1

    if response["status"] != "ok":
        print(f"Error: {response['message']}", file=sys.stderr)
        return 1

    data = response["data"]
    if data["is_valid"]:
        print("Configuration is valid")
        return 0
    print("Configuration is invalid", file=sys.stderr)
    for error in data.get("errors", []):
        print(f"  {error}", file=sys.stderr)
    return 1


def _cmd_config_reload(_args: argparse.Namespace) -> int:
    try:
        client = IPCClient()
        response = client.send_command("config_reload")
    except IPCConnectionError:
        print("Error: MouseFlow daemon is not running", file=sys.stderr)
        print("Start it with: mouseflow start", file=sys.stderr)
        return 1

    if response["status"] != "ok":
        print(f"Error: {response['message']}", file=sys.stderr)
        return 1

    data = response["data"]
    if data["success"]:
        print("Configuration reloaded successfully")
        return 0
    message = data.get("message", "Unknown error")
    print(f"Configuration reload failed: {message}", file=sys.stderr)
    return 1
