"""Tests for input engine gesture integration."""

from unittest.mock import MagicMock, patch

from evdev import ecodes

from mouseflow.domain import InputIdentifier, UserInput
from mouseflow.engine import read_events_with_gestures, to_movement_delta


class TestToMovementDelta:
    def test_rel_x_event(self) -> None:
        """Test REL_X event conversion."""
        event = MagicMock()
        event.type = ecodes.EV_REL
        event.code = ecodes.REL_X
        event.value = 10

        result = to_movement_delta(event)

        assert result == (10, 0)

    def test_rel_y_event(self) -> None:
        """Test REL_Y event conversion."""
        event = MagicMock()
        event.type = ecodes.EV_REL
        event.code = ecodes.REL_Y
        event.value = -5

        result = to_movement_delta(event)

        assert result == (0, -5)

    def test_non_movement_event(self) -> None:
        """Test non-movement event returns None."""
        event = MagicMock()
        event.type = ecodes.EV_KEY
        event.code = ecodes.BTN_SIDE
        event.value = 1

        result = to_movement_delta(event)

        assert result is None

    def test_rel_hwheel_event(self) -> None:
        """Test REL_HWHEEL event returns None (not a movement delta)."""
        event = MagicMock()
        event.type = ecodes.EV_REL
        event.code = ecodes.REL_HWHEEL
        event.value = 1

        result = to_movement_delta(event)

        assert result is None


class TestReadEventsWithGestures:
    @patch("mouseflow.engine.open_device")
    def test_button_event_yielded_when_not_in_gesture_mode(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test that button events are yielded when not in gesture mode."""
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        event = MagicMock()
        event.type = ecodes.EV_KEY
        event.code = ecodes.BTN_SIDE
        event.value = 1
        mock_device.read_loop.return_value = [event]

        events = list(read_events_with_gestures("/dev/input/event0"))

        assert len(events) == 1
        assert isinstance(events[0], UserInput)
        assert events[0].identifier == InputIdentifier.BTN_SIDE

    @patch("mouseflow.engine.open_device")
    def test_gesture_button_press_not_yielded(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test that gesture button press doesn't yield an event."""
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        event = MagicMock()
        event.type = ecodes.EV_KEY
        event.code = ecodes.BTN_EXTRA
        event.value = 1
        mock_device.read_loop.return_value = [event]

        events = list(read_events_with_gestures("/dev/input/event0"))

        assert len(events) == 0

    @patch("mouseflow.engine.open_device")
    def test_movement_events_not_yielded(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test that movement events are not yielded directly."""
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        event = MagicMock()
        event.type = ecodes.EV_REL
        event.code = ecodes.REL_X
        event.value = 10
        mock_device.read_loop.return_value = [event]

        events = list(read_events_with_gestures("/dev/input/event0"))

        assert len(events) == 0

    @patch("mouseflow.engine.open_device")
    def test_gesture_recognized_and_yielded(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test that a recognized gesture is yielded."""
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        events_input = []

        press_event = MagicMock()
        press_event.type = ecodes.EV_KEY
        press_event.code = ecodes.BTN_EXTRA
        press_event.value = 1
        events_input.append(press_event)

        for _ in range(10):
            move_event = MagicMock()
            move_event.type = ecodes.EV_REL
            move_event.code = ecodes.REL_X
            move_event.value = 10
            events_input.append(move_event)

        release_event = MagicMock()
        release_event.type = ecodes.EV_KEY
        release_event.code = ecodes.BTN_EXTRA
        release_event.value = 0
        events_input.append(release_event)

        mock_device.read_loop.return_value = events_input

        events = list(read_events_with_gestures("/dev/input/event0"))

        assert len(events) == 1
        assert isinstance(events[0], UserInput)
        assert events[0].identifier == InputIdentifier.GESTURE_RIGHT

    @patch("mouseflow.engine.open_device")
    def test_no_gesture_when_below_threshold(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test that no gesture is yielded when movement is below threshold."""
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        events_input = []

        press_event = MagicMock()
        press_event.type = ecodes.EV_KEY
        press_event.code = ecodes.BTN_EXTRA
        press_event.value = 1
        events_input.append(press_event)

        move_event = MagicMock()
        move_event.type = ecodes.EV_REL
        move_event.code = ecodes.REL_X
        move_event.value = 10
        events_input.append(move_event)

        release_event = MagicMock()
        release_event.type = ecodes.EV_KEY
        release_event.code = ecodes.BTN_EXTRA
        release_event.value = 0
        events_input.append(release_event)

        mock_device.read_loop.return_value = events_input

        events = list(read_events_with_gestures("/dev/input/event0"))

        assert len(events) == 0

    @patch("mouseflow.engine.open_device")
    def test_button_events_after_gesture_yielded(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test that button events after a gesture are yielded normally."""
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        events_input = []

        press_event = MagicMock()
        press_event.type = ecodes.EV_KEY
        press_event.code = ecodes.BTN_EXTRA
        press_event.value = 1
        events_input.append(press_event)

        for _ in range(10):
            move_event = MagicMock()
            move_event.type = ecodes.EV_REL
            move_event.code = ecodes.REL_X
            move_event.value = 10
            events_input.append(move_event)

        release_event = MagicMock()
        release_event.type = ecodes.EV_KEY
        release_event.code = ecodes.BTN_EXTRA
        release_event.value = 0
        events_input.append(release_event)

        side_event = MagicMock()
        side_event.type = ecodes.EV_KEY
        side_event.code = ecodes.BTN_SIDE
        side_event.value = 1
        events_input.append(side_event)

        mock_device.read_loop.return_value = events_input

        events = list(read_events_with_gestures("/dev/input/event0"))

        assert len(events) == 2
        assert isinstance(events[0], UserInput)
        assert events[0].identifier == InputIdentifier.GESTURE_RIGHT
        assert isinstance(events[1], UserInput)
        assert events[1].identifier == InputIdentifier.BTN_SIDE
