from __future__ import annotations

import sys
from typing import Any
from unittest.mock import patch

import pytest

from mouseflow.cli import (
    _cmd_config_reload,
    _cmd_devices,
    _cmd_status,
    _create_parser,
    _format_configuration,
    _format_devices,
    _format_status,
    main,
)
from mouseflow.ipc import IPCConnectionError


class TestCreateParser:
    def test_parser_has_version(self) -> None:
        parser = _create_parser()
        assert parser.prog == "mouseflow"

    def test_parser_has_start_command(self) -> None:
        parser = _create_parser()
        args = parser.parse_args(["start"])
        assert hasattr(args, "func")

    def test_parser_has_status_command(self) -> None:
        parser = _create_parser()
        args = parser.parse_args(["status"])
        assert hasattr(args, "func")

    def test_parser_has_devices_command(self) -> None:
        parser = _create_parser()
        args = parser.parse_args(["devices"])
        assert hasattr(args, "func")

    def test_parser_has_config_show_command(self) -> None:
        parser = _create_parser()
        args = parser.parse_args(["config", "show"])
        assert hasattr(args, "func")

    def test_parser_has_config_validate_command(self) -> None:
        parser = _create_parser()
        args = parser.parse_args(["config", "validate"])
        assert hasattr(args, "func")

    def test_parser_has_config_reload_command(self) -> None:
        parser = _create_parser()
        args = parser.parse_args(["config", "reload"])
        assert hasattr(args, "func")


class TestFormatStatus:
    def test_format_status_running(self, capsys: pytest.CaptureFixture[str]) -> None:
        data = {
            "is_running": True,
            "device_connected": True,
            "configuration_loaded": True,
            "active_profile": "firefox",
        }
        _format_status(data)
        captured = capsys.readouterr()
        assert "Running: yes" in captured.out
        assert "Device: connected" in captured.out
        assert "Configuration: loaded" in captured.out
        assert "Active profile: firefox" in captured.out

    def test_format_status_not_running(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        data = {
            "is_running": False,
            "device_connected": False,
            "configuration_loaded": False,
        }
        _format_status(data)
        captured = capsys.readouterr()
        assert "Running: no" in captured.out
        assert "Device: disconnected" in captured.out
        assert "Configuration: not loaded" in captured.out


class TestFormatDevices:
    def test_format_devices_with_active(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        devices = [
            {"name": "Mouse A", "path": "/dev/input/event0", "is_active": True},
            {"name": "Mouse B", "path": "/dev/input/event1", "is_active": False},
        ]
        _format_devices(devices)
        captured = capsys.readouterr()
        assert "Mouse A (active)" in captured.out
        assert "Mouse B" in captured.out
        assert "(active)" not in captured.out.split("Mouse B")[1].split("\n")[0]

    def test_format_devices_empty(self, capsys: pytest.CaptureFixture[str]) -> None:
        _format_devices([])
        captured = capsys.readouterr()
        assert captured.out == ""


class TestFormatConfiguration:
    def test_format_configuration_with_profiles(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_SIDE": {"type": "keyboard", "payload": "alt+left"},
                    },
                },
            ],
        }
        _format_configuration(config)
        captured = capsys.readouterr()
        assert "Profile: firefox" in captured.out
        assert "BTN_SIDE" in captured.out
        assert "alt+left" in captured.out

    def test_format_configuration_empty(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        config: dict[str, Any] = {"profiles": []}
        _format_configuration(config)
        captured = capsys.readouterr()
        assert "No profiles configured" in captured.out


class TestCmdStatus:
    def test_status_daemon_not_running(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with patch("mouseflow.cli.IPCClient") as mock_client:
            mock_client.return_value.send_command.side_effect = IPCConnectionError()
            import argparse

            args = argparse.Namespace()
            result = _cmd_status(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "daemon is not running" in captured.err

    def test_status_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("mouseflow.cli.IPCClient") as mock_client:
            mock_client.return_value.send_command.return_value = {
                "status": "ok",
                "data": {
                    "is_running": True,
                    "device_connected": True,
                    "configuration_loaded": True,
                    "active_profile": None,
                },
            }
            import argparse

            args = argparse.Namespace()
            result = _cmd_status(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Running: yes" in captured.out


class TestCmdDevices:
    def test_devices_daemon_not_running(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with patch("mouseflow.cli.IPCClient") as mock_client:
            mock_client.return_value.send_command.side_effect = IPCConnectionError()
            import argparse

            args = argparse.Namespace()
            result = _cmd_devices(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "daemon is not running" in captured.err

    def test_devices_no_devices(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("mouseflow.cli.IPCClient") as mock_client:
            mock_client.return_value.send_command.return_value = {
                "status": "ok",
                "data": [],
            }
            import argparse

            args = argparse.Namespace()
            result = _cmd_devices(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "No supported devices found" in captured.out

    def test_devices_with_devices(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("mouseflow.cli.IPCClient") as mock_client:
            mock_client.return_value.send_command.return_value = {
                "status": "ok",
                "data": [
                    {"name": "Mouse", "path": "/dev/input/event0", "is_active": True},
                ],
            }
            import argparse

            args = argparse.Namespace()
            result = _cmd_devices(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Mouse (active)" in captured.out


class TestCmdConfigReload:
    def test_reload_daemon_not_running(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with patch("mouseflow.cli.IPCClient") as mock_client:
            mock_client.return_value.send_command.side_effect = IPCConnectionError()
            import argparse

            args = argparse.Namespace()
            result = _cmd_config_reload(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "daemon is not running" in captured.err

    def test_reload_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("mouseflow.cli.IPCClient") as mock_client:
            mock_client.return_value.send_command.return_value = {
                "status": "ok",
                "data": {"success": True, "message": "Configuration reloaded"},
            }
            import argparse

            args = argparse.Namespace()
            result = _cmd_config_reload(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "reloaded successfully" in captured.out

    def test_reload_failure(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("mouseflow.cli.IPCClient") as mock_client:
            mock_client.return_value.send_command.return_value = {
                "status": "ok",
                "data": {"success": False, "message": "Invalid configuration"},
            }
            import argparse

            args = argparse.Namespace()
            result = _cmd_config_reload(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "reload failed" in captured.err


class TestMain:
    def test_main_no_args_shows_help(self) -> None:
        with patch.object(sys, "argv", ["mouseflow"]):
            result = main()
        assert result == 1

    def test_main_version(self) -> None:
        with (
            patch.object(sys, "argv", ["mouseflow", "--version"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()
        assert exc_info.value.code == 0
