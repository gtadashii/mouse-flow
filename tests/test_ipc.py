from __future__ import annotations

import socket
import threading
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from mouseflow.discovery import SupportedDevice
from mouseflow.domain import (
    Action,
    ActionType,
    Configuration,
    InputIdentifier,
    Profile,
)
from mouseflow.ipc import IPCClient, IPCConnectionError, IPCServer
from mouseflow.services import ApplicationServices


class MockStateProvider:
    def __init__(
        self,
        active_device: SupportedDevice | None = None,
        configuration: Configuration | None = None,
        config_path: Path | None = None,
    ) -> None:
        self._active_device = active_device
        self._configuration = configuration
        self._config_path = config_path or Path("/tmp/config.yaml")
        self._updated_config: Configuration | None = None

    @property
    def active_device(self) -> SupportedDevice | None:
        return self._active_device

    @property
    def configuration(self) -> Configuration | None:
        return self._configuration

    @property
    def config_path(self) -> Path:
        return self._config_path

    def update_configuration(self, config: Configuration) -> None:
        self._updated_config = config
        self._configuration = config


@pytest.fixture  # type: ignore[misc]
def socket_path(tmp_path: Path) -> Path:
    return tmp_path / "test.sock"


@pytest.fixture  # type: ignore[misc]
def mock_services() -> ApplicationServices:
    device = SupportedDevice(name="Test Mouse", path="/dev/input/event0")
    config = Configuration(
        profiles=(
            Profile(
                app_name="global",
                mappings={
                    InputIdentifier.BTN_SIDE: Action(
                        action_type=ActionType.KEYBOARD,
                        payload="alt+left",
                    ),
                },
            ),
        ),
    )
    state = MockStateProvider(active_device=device, configuration=config)
    return ApplicationServices(state_provider=state)


class TestIPCServer:
    def test_start_and_stop(
        self, socket_path: Path, mock_services: ApplicationServices
    ) -> None:
        server = IPCServer(services=mock_services, socket_path=socket_path)
        server.start()
        assert socket_path.exists()
        server.stop()
        assert not socket_path.exists()

    def test_dispatch_devices(
        self, socket_path: Path, mock_services: ApplicationServices
    ) -> None:
        with patch(
            "mouseflow.services.find_all_supported_devices",
            return_value=[SupportedDevice(name="Mouse", path="/dev/input/event0")],
        ):
            server = IPCServer(services=mock_services, socket_path=socket_path)
            server.start()
            try:
                client = IPCClient(socket_path=socket_path)
                response = client.send_command("devices")
                assert response["status"] == "ok"
                assert len(response["data"]) == 1
                assert response["data"][0]["name"] == "Mouse"
            finally:
                server.stop()

    def test_dispatch_status(
        self, socket_path: Path, mock_services: ApplicationServices
    ) -> None:
        server = IPCServer(services=mock_services, socket_path=socket_path)
        server.start()
        try:
            client = IPCClient(socket_path=socket_path)
            response = client.send_command("status")
            assert response["status"] == "ok"
            assert response["data"]["is_running"] is True
            assert response["data"]["device_connected"] is True
        finally:
            server.stop()

    def test_dispatch_config_show(
        self, socket_path: Path, mock_services: ApplicationServices
    ) -> None:
        server = IPCServer(services=mock_services, socket_path=socket_path)
        server.start()
        try:
            client = IPCClient(socket_path=socket_path)
            response = client.send_command("config_show")
            assert response["status"] == "ok"
            assert response["data"] is not None
            assert len(response["data"]["profiles"]) == 1
        finally:
            server.stop()

    def test_dispatch_config_reload(self, socket_path: Path, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n  BTN_SIDE:\n    type: keyboard\n    payload: alt+left\n"
        )
        state = MockStateProvider(config_path=config_file)
        services = ApplicationServices(state_provider=state)
        server = IPCServer(services=services, socket_path=socket_path)
        server.start()
        try:
            client = IPCClient(socket_path=socket_path)
            response = client.send_command("config_reload")
            assert response["status"] == "ok"
            assert response["data"]["success"] is True
        finally:
            server.stop()

    def test_dispatch_unknown_command(
        self, socket_path: Path, mock_services: ApplicationServices
    ) -> None:
        server = IPCServer(services=mock_services, socket_path=socket_path)
        server.start()
        try:
            client = IPCClient(socket_path=socket_path)
            response = client.send_command("unknown")
            assert response["status"] == "error"
            assert "Unknown command" in response["message"]
        finally:
            server.stop()

    def test_concurrent_connections(
        self, socket_path: Path, mock_services: ApplicationServices
    ) -> None:
        server = IPCServer(services=mock_services, socket_path=socket_path)
        server.start()
        try:
            results: list[dict[str, Any]] = []
            errors: list[Exception] = []

            def query() -> None:
                try:
                    client = IPCClient(socket_path=socket_path)
                    response = client.send_command("status")
                    results.append(response)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=query) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=5.0)

            assert len(errors) == 0
            assert len(results) == 5
            for r in results:
                assert r["status"] == "ok"
        finally:
            server.stop()

    def test_stale_socket_cleanup(
        self, socket_path: Path, mock_services: ApplicationServices
    ) -> None:
        socket_path.parent.mkdir(parents=True, exist_ok=True)
        socket_path.touch()
        assert socket_path.exists()

        server = IPCServer(services=mock_services, socket_path=socket_path)
        server.start()
        assert socket_path.exists()
        server.stop()


class TestIPCClient:
    def test_connection_error_no_socket(self, tmp_path: Path) -> None:
        socket_path = tmp_path / "nonexistent.sock"
        client = IPCClient(socket_path=socket_path)
        with pytest.raises(IPCConnectionError, match="Daemon not running"):
            client.send_command("status")

    def test_connection_error_stopped_daemon(self, socket_path: Path) -> None:
        socket_path.parent.mkdir(parents=True, exist_ok=True)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(str(socket_path))
        sock.listen(1)
        sock.close()

        client = IPCClient(socket_path=socket_path)
        with pytest.raises(IPCConnectionError):
            client.send_command("status")

        if socket_path.exists():
            socket_path.unlink()
