from __future__ import annotations

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
from mouseflow.ipc import IPCClient, IPCServer
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
    return tmp_path / "integration_test.sock"


@pytest.fixture  # type: ignore[misc]
def full_config() -> Configuration:
    return Configuration(
        profiles=(
            Profile(
                app_name="firefox",
                mappings={
                    InputIdentifier.BTN_SIDE: Action(
                        action_type=ActionType.KEYBOARD,
                        payload="alt+left",
                    ),
                    InputIdentifier.BTN_EXTRA: Action(
                        action_type=ActionType.KEYBOARD,
                        payload="alt+right",
                    ),
                },
            ),
            Profile(
                app_name="global",
                mappings={
                    InputIdentifier.BTN_SIDE: Action(
                        action_type=ActionType.KEYBOARD,
                        payload="ctrl+c",
                    ),
                },
            ),
        ),
    )


class TestFullIPCWorkflow:
    def test_status_query(
        self,
        socket_path: Path,
        full_config: Configuration,
    ) -> None:
        device = SupportedDevice(name="Test Mouse", path="/dev/input/event0")
        state = MockStateProvider(active_device=device, configuration=full_config)
        services = ApplicationServices(state_provider=state)
        server = IPCServer(services=services, socket_path=socket_path)
        server.start()

        try:
            client = IPCClient(socket_path=socket_path)
            response = client.send_command("status")

            assert response["status"] == "ok"
            data = response["data"]
            assert data["is_running"] is True
            assert data["device_connected"] is True
            assert data["configuration_loaded"] is True
        finally:
            server.stop()

    def test_devices_query(
        self,
        socket_path: Path,
        full_config: Configuration,
    ) -> None:
        device = SupportedDevice(name="Test Mouse", path="/dev/input/event0")
        state = MockStateProvider(active_device=device, configuration=full_config)
        services = ApplicationServices(state_provider=state)
        server = IPCServer(services=services, socket_path=socket_path)
        server.start()

        try:
            with patch(
                "mouseflow.services.find_all_supported_devices",
                return_value=[device],
            ):
                client = IPCClient(socket_path=socket_path)
                response = client.send_command("devices")

            assert response["status"] == "ok"
            devices = response["data"]
            assert len(devices) == 1
            assert devices[0]["name"] == "Test Mouse"
            assert devices[0]["is_active"] is True
        finally:
            server.stop()

    def test_config_show_query(
        self,
        socket_path: Path,
        full_config: Configuration,
    ) -> None:
        state = MockStateProvider(configuration=full_config)
        services = ApplicationServices(state_provider=state)
        server = IPCServer(services=services, socket_path=socket_path)
        server.start()

        try:
            client = IPCClient(socket_path=socket_path)
            response = client.send_command("config_show")

            assert response["status"] == "ok"
            config = response["data"]
            assert config is not None
            assert len(config["profiles"]) == 2
        finally:
            server.stop()

    def test_config_reload_workflow(
        self,
        socket_path: Path,
        tmp_path: Path,
    ) -> None:
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
            data = response["data"]
            assert data["success"] is True
            assert state._updated_config is not None
        finally:
            server.stop()

    def test_concurrent_queries(
        self,
        socket_path: Path,
        full_config: Configuration,
    ) -> None:
        device = SupportedDevice(name="Test Mouse", path="/dev/input/event0")
        state = MockStateProvider(active_device=device, configuration=full_config)
        services = ApplicationServices(state_provider=state)
        server = IPCServer(services=services, socket_path=socket_path)
        server.start()

        try:
            results: list[dict[str, Any]] = []
            errors: list[Exception] = []

            def query_status() -> None:
                try:
                    client = IPCClient(socket_path=socket_path)
                    response = client.send_command("status")
                    results.append(response)
                except Exception as e:
                    errors.append(e)

            def query_devices() -> None:
                try:
                    with patch(
                        "mouseflow.services.find_all_supported_devices",
                        return_value=[device],
                    ):
                        client = IPCClient(socket_path=socket_path)
                        response = client.send_command("devices")
                        results.append(response)
                except Exception as e:
                    errors.append(e)

            threads = [
                threading.Thread(target=query_status),
                threading.Thread(target=query_devices),
                threading.Thread(target=query_status),
                threading.Thread(target=query_devices),
                threading.Thread(target=query_status),
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=10.0)

            assert len(errors) == 0
            assert len(results) == 5
        finally:
            server.stop()

    def test_error_handling_unknown_command(
        self,
        socket_path: Path,
        full_config: Configuration,
    ) -> None:
        state = MockStateProvider(configuration=full_config)
        services = ApplicationServices(state_provider=state)
        server = IPCServer(services=services, socket_path=socket_path)
        server.start()

        try:
            client = IPCClient(socket_path=socket_path)
            response = client.send_command("nonexistent_command")

            assert response["status"] == "error"
            assert "Unknown command" in response["message"]
        finally:
            server.stop()

    def test_config_validate_invalid(
        self,
        socket_path: Path,
        tmp_path: Path,
    ) -> None:
        config_file = tmp_path / "invalid_config.yaml"
        config_file.write_text("invalid: true\n")

        state = MockStateProvider(config_path=config_file)
        services = ApplicationServices(state_provider=state)
        server = IPCServer(services=services, socket_path=socket_path)
        server.start()

        try:
            client = IPCClient(socket_path=socket_path)
            response = client.send_command(
                "config_validate",
                {"path": str(config_file)},
            )

            assert response["status"] == "ok"
            data = response["data"]
            assert data["is_valid"] is False
            assert len(data["errors"]) > 0
        finally:
            server.stop()
