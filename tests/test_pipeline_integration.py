"""Integration tests for the pipeline architecture."""

from unittest.mock import MagicMock, patch

from evdev import ecodes

from mouseflow.domain import (
    Application,
    DispatchContext,
    MouseEvent,
    Window,
    WindowInfo,
)
from mouseflow.engine import read_events


def _make_event(event_type: int, code: int, value: int = 1) -> MagicMock:
    event = MagicMock()
    event.type = event_type
    event.code = code
    event.value = value
    return event


class TestPipelineIntegration:
    """Test the complete pipeline from raw events to dispatch context."""

    @patch("mouseflow.engine.InputDevice")
    def test_event_to_dispatch_context(self, mock_input_device: MagicMock) -> None:
        """Test that raw events can be converted to DispatchContext."""
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        event = _make_event(ecodes.EV_KEY, ecodes.BTN_SIDE, 1)
        mock_device.read_loop.return_value = iter([event])

        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        window_info = WindowInfo(application=app, window=window)

        events = list(read_events("/dev/input/event0"))
        assert len(events) == 1

        context = DispatchContext(event=events[0], window_info=window_info)
        assert isinstance(context.event, MouseEvent)
        assert context.event.button is not None
        assert context.event.button.value == "BTN_SIDE"
        assert context.window_info is not None
        assert context.window_info.application.app_name == "Firefox"
        assert context.window_info.window.title == "ChatGPT"

    @patch("mouseflow.engine.InputDevice")
    def test_pipeline_with_multiple_events(self, mock_input_device: MagicMock) -> None:
        """Test pipeline with multiple events."""
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        events_input = [
            _make_event(ecodes.EV_KEY, ecodes.BTN_SIDE, 1),
            _make_event(ecodes.EV_KEY, ecodes.BTN_EXTRA, 1),
            _make_event(ecodes.EV_REL, ecodes.REL_HWHEEL, 1),
        ]
        mock_device.read_loop.return_value = iter(events_input)

        app = Application(app_name="VSCode")
        window = Window(title="main.py")
        window_info = WindowInfo(application=app, window=window)

        events = list(read_events("/dev/input/event0"))
        assert len(events) == 3

        contexts = [
            DispatchContext(event=event, window_info=window_info) for event in events
        ]

        assert len(contexts) == 3
        assert isinstance(contexts[0].event, MouseEvent)
        assert contexts[0].event.button is not None
        assert contexts[0].event.button.value == "BTN_SIDE"
        assert isinstance(contexts[1].event, MouseEvent)
        assert contexts[1].event.button is not None
        assert contexts[1].event.button.value == "BTN_EXTRA"
        assert isinstance(contexts[2].event, MouseEvent)
        assert contexts[2].event.wheel is not None
        assert contexts[2].event.wheel.value == "REL_HWHEEL"

        for context in contexts:
            assert context.window_info is not None
            assert context.window_info.application.app_name == "VSCode"

    @patch("mouseflow.engine.InputDevice")
    def test_pipeline_with_none_window_info(self, mock_input_device: MagicMock) -> None:
        """Test pipeline when window resolution fails."""
        mock_device = MagicMock()
        mock_input_device.return_value = mock_device

        event = _make_event(ecodes.EV_KEY, ecodes.BTN_SIDE, 1)
        mock_device.read_loop.return_value = iter([event])

        events = list(read_events("/dev/input/event0"))
        assert len(events) == 1

        context = DispatchContext(event=events[0], window_info=None)
        assert isinstance(context.event, MouseEvent)
        assert context.event.button is not None
        assert context.event.button.value == "BTN_SIDE"
        assert context.window_info is None
