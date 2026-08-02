from __future__ import annotations

from unittest.mock import MagicMock, patch

from evdev import ecodes

from mouseflow.engine import (
    SUPPORTED_EVENTS,
    get_event_name,
    is_supported_event,
    open_device,
    read_events,
)


def _make_event(event_type: int, code: int, value: int = 1) -> MagicMock:
    event = MagicMock()
    event.type = event_type
    event.code = code
    event.value = value
    return event


class TestIsSupportedEvent:
    def test_btn_side_is_supported(self) -> None:
        event = _make_event(ecodes.EV_KEY, ecodes.BTN_SIDE)
        assert is_supported_event(event) is True

    def test_btn_extra_is_supported(self) -> None:
        event = _make_event(ecodes.EV_KEY, ecodes.BTN_EXTRA)
        assert is_supported_event(event) is True

    def test_btn_forward_is_supported(self) -> None:
        event = _make_event(ecodes.EV_KEY, ecodes.BTN_FORWARD)
        assert is_supported_event(event) is True

    def test_rel_hwheel_is_supported(self) -> None:
        event = _make_event(ecodes.EV_REL, ecodes.REL_HWHEEL)
        assert is_supported_event(event) is True

    def test_btn_left_is_not_supported(self) -> None:
        event = _make_event(ecodes.EV_KEY, ecodes.BTN_LEFT)
        assert is_supported_event(event) is False

    def test_btn_right_is_not_supported(self) -> None:
        event = _make_event(ecodes.EV_KEY, ecodes.BTN_RIGHT)
        assert is_supported_event(event) is False

    def test_rel_x_is_not_supported(self) -> None:
        event = _make_event(ecodes.EV_REL, ecodes.REL_X)
        assert is_supported_event(event) is False

    def test_rel_y_is_not_supported(self) -> None:
        event = _make_event(ecodes.EV_REL, ecodes.REL_Y)
        assert is_supported_event(event) is False

    def test_unknown_event_type_is_not_supported(self) -> None:
        event = _make_event(0xFF, 0x00)
        assert is_supported_event(event) is False


class TestGetEventName:
    def test_btn_side_name(self) -> None:
        event = _make_event(ecodes.EV_KEY, ecodes.BTN_SIDE)
        assert get_event_name(event) == "BTN_SIDE"

    def test_btn_extra_name(self) -> None:
        event = _make_event(ecodes.EV_KEY, ecodes.BTN_EXTRA)
        assert get_event_name(event) == "BTN_EXTRA"

    def test_btn_forward_name(self) -> None:
        event = _make_event(ecodes.EV_KEY, ecodes.BTN_FORWARD)
        assert get_event_name(event) == "BTN_FORWARD"

    def test_rel_hwheel_name(self) -> None:
        event = _make_event(ecodes.EV_REL, ecodes.REL_HWHEEL)
        assert get_event_name(event) == "REL_HWHEEL"

    def test_unknown_key_code(self) -> None:
        event = _make_event(ecodes.EV_KEY, 0xFFFF)
        assert get_event_name(event) == "UNKNOWN_KEY_65535"

    def test_unknown_rel_code(self) -> None:
        event = _make_event(ecodes.EV_REL, 0xFFFF)
        assert get_event_name(event) == "UNKNOWN_REL_65535"

    def test_unknown_event_type(self) -> None:
        event = _make_event(0xFF, 0x00)
        assert get_event_name(event) == "UNKNOWN_255_0"


class TestOpenDevice:
    @patch("mouseflow.engine.InputDevice")
    def test_open_device_success(self, mock_input_device: MagicMock) -> None:
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        device = open_device("/dev/input/event0")

        assert device == mock_device
        mock_input_device.assert_called_once_with("/dev/input/event0")

    @patch("mouseflow.engine.InputDevice")
    def test_open_device_failure(self, mock_input_device: MagicMock) -> None:
        mock_input_device.side_effect = OSError("Permission denied")

        try:
            open_device("/dev/input/event0")
            raise AssertionError("Should have exited")
        except SystemExit as e:
            assert e.code == 1


class TestSupportedEventsConfiguration:
    def test_supported_events_contains_btn_side(self) -> None:
        assert ecodes.BTN_SIDE in SUPPORTED_EVENTS[ecodes.EV_KEY]

    def test_supported_events_contains_btn_extra(self) -> None:
        assert ecodes.BTN_EXTRA in SUPPORTED_EVENTS[ecodes.EV_KEY]

    def test_supported_events_contains_btn_forward(self) -> None:
        assert ecodes.BTN_FORWARD in SUPPORTED_EVENTS[ecodes.EV_KEY]

    def test_supported_events_contains_rel_hwheel(self) -> None:
        assert ecodes.REL_HWHEEL in SUPPORTED_EVENTS[ecodes.EV_REL]


class TestReadEvents:
    @patch("mouseflow.engine.InputDevice")
    def test_read_events_yields_button_event(
        self, mock_input_device: MagicMock
    ) -> None:
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        event = _make_event(ecodes.EV_KEY, ecodes.BTN_SIDE, 1)
        mock_device.read_loop.return_value = iter([event])

        events = list(read_events("/dev/input/event0"))

        assert len(events) == 1
        assert events[0].event_type.value == "BUTTON"
        assert events[0].button is not None
        assert events[0].button.value == "BTN_SIDE"
        assert events[0].value == 1

    @patch("mouseflow.engine.InputDevice")
    def test_read_events_yields_wheel_event(self, mock_input_device: MagicMock) -> None:
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        event = _make_event(ecodes.EV_REL, ecodes.REL_HWHEEL, 1)
        mock_device.read_loop.return_value = iter([event])

        events = list(read_events("/dev/input/event0"))

        assert len(events) == 1
        assert events[0].event_type.value == "WHEEL"
        assert events[0].wheel is not None
        assert events[0].wheel.value == "REL_HWHEEL"
        assert events[0].value == 1

    @patch("mouseflow.engine.InputDevice")
    def test_read_events_filters_unsupported_events(
        self, mock_input_device: MagicMock
    ) -> None:
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        supported_event = _make_event(ecodes.EV_KEY, ecodes.BTN_SIDE, 1)
        unsupported_event = _make_event(ecodes.EV_KEY, ecodes.BTN_LEFT, 1)
        mock_device.read_loop.return_value = iter([unsupported_event, supported_event])

        events = list(read_events("/dev/input/event0"))

        assert len(events) == 1
        assert events[0].button is not None
        assert events[0].button.value == "BTN_SIDE"

    @patch("mouseflow.engine.InputDevice")
    def test_read_events_multiple_events(self, mock_input_device: MagicMock) -> None:
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        events_input = [
            _make_event(ecodes.EV_KEY, ecodes.BTN_SIDE, 1),
            _make_event(ecodes.EV_KEY, ecodes.BTN_EXTRA, 1),
            _make_event(ecodes.EV_REL, ecodes.REL_HWHEEL, 1),
        ]
        mock_device.read_loop.return_value = iter(events_input)

        events = list(read_events("/dev/input/event0"))

        assert len(events) == 3
        assert events[0].button is not None
        assert events[0].button.value == "BTN_SIDE"
        assert events[1].button is not None
        assert events[1].button.value == "BTN_EXTRA"
        assert events[2].wheel is not None
        assert events[2].wheel.value == "REL_HWHEEL"
