from __future__ import annotations

from unittest.mock import MagicMock, patch

from evdev.ecodes import BTN_EXTRA, BTN_LEFT, BTN_RIGHT, BTN_SIDE, REL_X, REL_Y

from mouseflow.discovery import (
    SupportedDevice,
    enumerate_devices,
    find_supported_device,
    format_found,
    format_not_found,
    is_supported_device,
)


def _make_mock_device(
    name: str = "Test Mouse",
    path: str = "/dev/input/event0",
    buttons: set[int] | None = None,
    relative: set[int] | None = None,
) -> MagicMock:
    device = MagicMock()
    device.name = name
    device.path = path

    caps: dict[int, list[int]] = {}
    if buttons is not None:
        caps[0x01] = list(buttons)
    if relative is not None:
        caps[0x02] = list(relative)

    device.capabilities.return_value = caps
    return device


class TestIsSupportedDevice:
    def test_supported_mouse_with_side_button(self) -> None:
        device = _make_mock_device(
            buttons={BTN_LEFT, BTN_RIGHT, BTN_SIDE},
            relative={REL_X, REL_Y},
        )
        assert is_supported_device(device) is True

    def test_supported_mouse_with_extra_button(self) -> None:
        device = _make_mock_device(
            buttons={BTN_LEFT, BTN_RIGHT, BTN_EXTRA},
            relative={REL_X, REL_Y},
        )
        assert is_supported_device(device) is True

    def test_unsupported_missing_side_buttons(self) -> None:
        device = _make_mock_device(
            buttons={BTN_LEFT, BTN_RIGHT},
            relative={REL_X, REL_Y},
        )
        assert is_supported_device(device) is False

    def test_unsupported_missing_right_button(self) -> None:
        device = _make_mock_device(
            buttons={BTN_LEFT, BTN_SIDE},
            relative={REL_X, REL_Y},
        )
        assert is_supported_device(device) is False

    def test_unsupported_missing_relative_axes(self) -> None:
        device = _make_mock_device(
            buttons={BTN_LEFT, BTN_RIGHT, BTN_SIDE},
            relative=set(),
        )
        assert is_supported_device(device) is False

    def test_unsupported_keyboard(self) -> None:
        device = _make_mock_device(
            buttons=set(),
            relative=set(),
        )
        assert is_supported_device(device) is False


class TestEnumerateDevices:
    @patch("mouseflow.discovery.list_devices")
    @patch("mouseflow.discovery.InputDevice")
    def test_enumerates_devices_sorted(
        self, mock_input_device: MagicMock, mock_list: MagicMock
    ) -> None:
        mock_list.return_value = ["/dev/input/event1", "/dev/input/event0"]
        mock_input_device.side_effect = lambda path: _make_mock_device(path=path)

        devices = enumerate_devices()

        assert len(devices) == 2
        assert devices[0].path == "/dev/input/event0"
        assert devices[1].path == "/dev/input/event1"

    @patch("mouseflow.discovery.list_devices")
    @patch("mouseflow.discovery.InputDevice")
    def test_skips_inaccessible_devices(
        self, mock_input_device: MagicMock, mock_list: MagicMock
    ) -> None:
        mock_list.return_value = ["/dev/input/event0", "/dev/input/event1"]
        mock_input_device.side_effect = [
            PermissionError("no access"),
            _make_mock_device(path="/dev/input/event1"),
        ]

        devices = enumerate_devices()

        assert len(devices) == 1
        assert devices[0].path == "/dev/input/event1"

    @patch("mouseflow.discovery.list_devices")
    def test_returns_empty_when_no_devices(self, mock_list: MagicMock) -> None:
        mock_list.return_value = []

        devices = enumerate_devices()

        assert devices == []


class TestFindSupportedDevice:
    @patch("mouseflow.discovery.enumerate_devices")
    def test_returns_first_supported_device(self, mock_enumerate: MagicMock) -> None:
        unsupported = _make_mock_device(
            name="Keyboard",
            path="/dev/input/event0",
            buttons=set(),
            relative=set(),
        )
        supported = _make_mock_device(
            name="Logitech MX Master 3S",
            path="/dev/input/event1",
            buttons={BTN_LEFT, BTN_RIGHT, BTN_SIDE},
            relative={REL_X, REL_Y},
        )
        mock_enumerate.return_value = [unsupported, supported]

        result = find_supported_device()

        assert result is not None
        assert result.name == "Logitech MX Master 3S"
        assert result.path == "/dev/input/event1"

    @patch("mouseflow.discovery.enumerate_devices")
    def test_returns_none_when_no_supported_device(
        self, mock_enumerate: MagicMock
    ) -> None:
        unsupported = _make_mock_device(
            name="Keyboard",
            path="/dev/input/event0",
            buttons=set(),
            relative=set(),
        )
        mock_enumerate.return_value = [unsupported]

        result = find_supported_device()

        assert result is None

    @patch("mouseflow.discovery.enumerate_devices")
    def test_returns_none_when_no_devices(self, mock_enumerate: MagicMock) -> None:
        mock_enumerate.return_value = []

        result = find_supported_device()

        assert result is None


class TestFormatMessages:
    def test_format_found(self) -> None:
        device = SupportedDevice(name="Logitech MX Master 3S", path="/dev/input/event0")
        assert format_found(device) == "Found device:\n\nLogitech MX Master 3S"

    def test_format_not_found(self) -> None:
        assert format_not_found() == "No supported mouse found."
