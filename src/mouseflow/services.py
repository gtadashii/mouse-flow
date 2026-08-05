from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from mouseflow.discovery import SupportedDevice, find_all_supported_devices
from mouseflow.domain import (
    ApplicationStatus,
    Configuration,
    DeviceInfo,
    ReloadResult,
    ValidationResult,
)
from mouseflow.parser import ConfigurationError, parse_config


class DaemonStateProvider(Protocol):
    @property
    def active_device(self) -> SupportedDevice | None: ...
    @property
    def configuration(self) -> Configuration | None: ...
    @property
    def config_path(self) -> Path: ...
    def update_configuration(self, config: Configuration) -> None: ...


@dataclass(frozen=True)
class ApplicationServices:
    state_provider: DaemonStateProvider

    def list_devices(self) -> list[DeviceInfo]:
        all_devices = find_all_supported_devices()
        active = self.state_provider.active_device
        return [
            DeviceInfo(
                path=device.path,
                name=device.name,
                is_active=(active is not None and device.path == active.path),
            )
            for device in all_devices
        ]

    def get_status(self) -> ApplicationStatus:
        device = self.state_provider.active_device
        config = self.state_provider.configuration
        return ApplicationStatus(
            is_running=True,
            device_connected=(device is not None),
            configuration_loaded=(config is not None),
            active_profile=None,
        )

    def get_configuration(self) -> Configuration | None:
        return self.state_provider.configuration

    def validate_configuration(self, path: Path | None = None) -> ValidationResult:
        if path is None:
            path = self.state_provider.config_path
        if not path.exists():
            return ValidationResult(
                is_valid=False,
                errors=(f"Configuration file not found: {path}",),
            )
        try:
            parse_config(path)
            return ValidationResult(is_valid=True)
        except ConfigurationError as e:
            return ValidationResult(is_valid=False, errors=(str(e),))

    def reload_configuration(self) -> ReloadResult:
        try:
            new_config = parse_config(self.state_provider.config_path)
            self.state_provider.update_configuration(new_config)
            return ReloadResult(success=True, message="Configuration reloaded")
        except ConfigurationError as e:
            return ReloadResult(success=False, message=str(e))
