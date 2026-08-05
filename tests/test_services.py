from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from mouseflow.discovery import SupportedDevice
from mouseflow.domain import (
    Configuration,
    DeviceInfo,
    Profile,
)
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
        self._config_path = (
            config_path or Path.home() / ".config" / "mouseflow" / "config.yaml"
        )
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


class TestApplicationServicesListDevices:
    def test_list_devices_with_active_device(self) -> None:
        device1 = SupportedDevice(name="Mouse A", path="/dev/input/event0")
        device2 = SupportedDevice(name="Mouse B", path="/dev/input/event1")
        state = MockStateProvider(active_device=device1)

        with patch(
            "mouseflow.services.find_all_supported_devices",
            return_value=[device1, device2],
        ):
            services = ApplicationServices(state_provider=state)
            result = services.list_devices()

        assert len(result) == 2
        assert result[0] == DeviceInfo(
            path="/dev/input/event0", name="Mouse A", is_active=True
        )
        assert result[1] == DeviceInfo(
            path="/dev/input/event1", name="Mouse B", is_active=False
        )

    def test_list_devices_with_no_active_device(self) -> None:
        device1 = SupportedDevice(name="Mouse A", path="/dev/input/event0")
        state = MockStateProvider(active_device=None)

        with patch(
            "mouseflow.services.find_all_supported_devices",
            return_value=[device1],
        ):
            services = ApplicationServices(state_provider=state)
            result = services.list_devices()

        assert len(result) == 1
        assert result[0].is_active is False

    def test_list_devices_empty(self) -> None:
        state = MockStateProvider(active_device=None)

        with patch(
            "mouseflow.services.find_all_supported_devices",
            return_value=[],
        ):
            services = ApplicationServices(state_provider=state)
            result = services.list_devices()

        assert result == []


class TestApplicationServicesGetStatus:
    def test_get_status_fully_operational(self) -> None:
        device = SupportedDevice(name="Mouse", path="/dev/input/event0")
        config = Configuration(profiles=(Profile(app_name="global", mappings={}),))
        state = MockStateProvider(active_device=device, configuration=config)
        services = ApplicationServices(state_provider=state)

        result = services.get_status()

        assert result.is_running is True
        assert result.device_connected is True
        assert result.configuration_loaded is True
        assert result.active_profile is None

    def test_get_status_no_device(self) -> None:
        config = Configuration(profiles=(Profile(app_name="global", mappings={}),))
        state = MockStateProvider(active_device=None, configuration=config)
        services = ApplicationServices(state_provider=state)

        result = services.get_status()

        assert result.is_running is True
        assert result.device_connected is False
        assert result.configuration_loaded is True

    def test_get_status_no_configuration(self) -> None:
        device = SupportedDevice(name="Mouse", path="/dev/input/event0")
        state = MockStateProvider(active_device=device, configuration=None)
        services = ApplicationServices(state_provider=state)

        result = services.get_status()

        assert result.is_running is True
        assert result.device_connected is True
        assert result.configuration_loaded is False


class TestApplicationServicesGetConfiguration:
    def test_get_configuration_loaded(self) -> None:
        config = Configuration(profiles=(Profile(app_name="global", mappings={}),))
        state = MockStateProvider(configuration=config)
        services = ApplicationServices(state_provider=state)

        result = services.get_configuration()

        assert result == config

    def test_get_configuration_none(self) -> None:
        state = MockStateProvider(configuration=None)
        services = ApplicationServices(state_provider=state)

        result = services.get_configuration()

        assert result is None


class TestApplicationServicesValidateConfiguration:
    def test_validate_valid_file(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n  BTN_SIDE:\n    type: keyboard\n    payload: alt+left\n"
        )
        state = MockStateProvider(config_path=config_file)
        services = ApplicationServices(state_provider=state)

        result = services.validate_configuration(config_file)

        assert result.is_valid is True
        assert result.errors == ()

    def test_validate_invalid_file(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: true\n")
        state = MockStateProvider(config_path=config_file)
        services = ApplicationServices(state_provider=state)

        result = services.validate_configuration(config_file)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_nonexistent_file(self, tmp_path: Path) -> None:
        config_file = tmp_path / "nonexistent.yaml"
        state = MockStateProvider(config_path=config_file)
        services = ApplicationServices(state_provider=state)

        result = services.validate_configuration(config_file)

        assert result.is_valid is False
        assert "not found" in result.errors[0]

    def test_validate_default_path(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n  BTN_SIDE:\n    type: keyboard\n    payload: alt+left\n"
        )
        state = MockStateProvider(config_path=config_file)
        services = ApplicationServices(state_provider=state)

        result = services.validate_configuration()

        assert result.is_valid is True


class TestApplicationServicesReloadConfiguration:
    def test_reload_success(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n  BTN_SIDE:\n    type: keyboard\n    payload: alt+left\n"
        )
        state = MockStateProvider(config_path=config_file)
        services = ApplicationServices(state_provider=state)

        result = services.reload_configuration()

        assert result.success is True
        assert state._updated_config is not None

    def test_reload_failure(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: true\n")
        state = MockStateProvider(config_path=config_file)
        services = ApplicationServices(state_provider=state)

        result = services.reload_configuration()

        assert result.success is False
        assert result.message is not None
        assert state._updated_config is None
