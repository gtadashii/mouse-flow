from __future__ import annotations

from dataclasses import dataclass

from evdev import InputDevice, list_devices
from evdev.ecodes import BTN_EXTRA, BTN_LEFT, BTN_RIGHT, BTN_SIDE, REL_X, REL_Y


@dataclass(frozen=True)
class SupportedDevice:
    name: str
    path: str


_REQUIRED_BUTTONS: frozenset[int] = frozenset({BTN_LEFT, BTN_RIGHT})
_SIDE_BUTTONS: frozenset[int] = frozenset({BTN_SIDE, BTN_EXTRA})
_REQUIRED_RELATIVE: frozenset[int] = frozenset({REL_X, REL_Y})


def _get_capabilities(device: InputDevice[str]) -> tuple[set[int], set[int]]:
    caps = device.capabilities(absinfo=False, verbose=False)
    buttons: set[int] = set(caps.get(0x01, []))
    relative: set[int] = set(caps.get(0x02, []))
    return buttons, relative


def is_supported_device(device: InputDevice[str]) -> bool:
    buttons, relative = _get_capabilities(device)
    has_basic_buttons = _REQUIRED_BUTTONS.issubset(buttons)
    has_side_button = bool(buttons & _SIDE_BUTTONS)
    has_relative = _REQUIRED_RELATIVE.issubset(relative)
    return has_basic_buttons and has_side_button and has_relative


def enumerate_devices() -> list[InputDevice[str]]:
    paths = list_devices()
    devices: list[InputDevice[str]] = []
    for path in sorted(paths):
        try:
            devices.append(InputDevice(path))
        except (OSError, PermissionError):
            continue
    return devices


def find_supported_device() -> SupportedDevice | None:
    for device in enumerate_devices():
        if is_supported_device(device):
            return SupportedDevice(name=device.name, path=device.path)
    return None


def find_all_supported_devices() -> list[SupportedDevice]:
    devices: list[SupportedDevice] = []
    for device in enumerate_devices():
        if is_supported_device(device):
            devices.append(SupportedDevice(name=device.name, path=device.path))
    return devices


def format_found(device: SupportedDevice) -> str:
    return f"Found device:\n\n{device.name}"


def format_not_found() -> str:
    return "No supported mouse found."
