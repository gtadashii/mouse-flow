from __future__ import annotations

from collections.abc import Iterable

from mouseflow.dispatcher import EventDispatcher, format_dispatch_context
from mouseflow.domain import (
    Application,
    DispatchContext,
    EventType,
    MouseButton,
    MouseEvent,
    WheelAxis,
    Window,
    WindowInfo,
)


class MockResolver:
    """Mock WindowResolver for testing."""

    def __init__(self, window_info: WindowInfo | None = None) -> None:
        self._window_info = window_info
        self.resolve_call_count = 0

    def resolve(self) -> WindowInfo | None:
        self.resolve_call_count += 1
        return self._window_info


class TestEventDispatcher:
    def test_dispatch_with_window_info(self) -> None:
        """Test dispatch with successful window resolution."""
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        window_info = WindowInfo(application=app, window=window)

        resolver = MockResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        events = iter([event])

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert contexts[0].event == event
        assert contexts[0].window_info == window_info
        assert resolver.resolve_call_count == 1

    def test_dispatch_without_window_info(self) -> None:
        """Test dispatch when window resolution fails."""
        resolver = MockResolver(window_info=None)
        dispatcher = EventDispatcher(resolver)

        event = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        events = iter([event])

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert contexts[0].event == event
        assert contexts[0].window_info is None
        assert resolver.resolve_call_count == 1

    def test_dispatch_multiple_events(self) -> None:
        """Test dispatch with multiple events."""
        app = Application(app_name="VSCode")
        window = Window(title="main.py")
        window_info = WindowInfo(application=app, window=window)

        resolver = MockResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        event1 = MouseEvent.button_event(MouseButton.BTN_SIDE)
        event2 = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        event3 = MouseEvent.wheel_event(WheelAxis.REL_HWHEEL, 1)
        events = iter([event1, event2, event3])

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 3
        assert contexts[0].event == event1
        assert contexts[1].event == event2
        assert contexts[2].event == event3
        assert resolver.resolve_call_count == 3

    def test_dispatch_empty_events(self) -> None:
        """Test dispatch with no events."""
        resolver = MockResolver()
        dispatcher = EventDispatcher(resolver)

        events: Iterable[MouseEvent] = iter([])
        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 0
        assert resolver.resolve_call_count == 0

    def test_dispatch_independence(self) -> None:
        """Test that each event is processed independently."""
        resolver = MockResolver()
        dispatcher = EventDispatcher(resolver)

        event1 = MouseEvent.button_event(MouseButton.BTN_SIDE)
        event2 = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        events = iter([event1, event2])

        contexts = list(dispatcher.dispatch(events))

        # Each event should have its own context
        assert contexts[0].event == event1
        assert contexts[1].event == event2
        assert contexts[0] != contexts[1]


class TestFormatDispatchContext:
    def test_format_with_window_info(self) -> None:
        """Test formatting with window info."""
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        window_info = WindowInfo(application=app, window=window)
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        context = DispatchContext(event=event, window_info=window_info)

        result = format_dispatch_context(context)

        assert result == "Application: Firefox\nTitle: ChatGPT\nEvent: BTN_SIDE"

    def test_format_without_window_info(self) -> None:
        """Test formatting without window info."""
        event = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        context = DispatchContext(event=event, window_info=None)

        result = format_dispatch_context(context)

        assert result == "Application: Unknown\nTitle: Unknown\nEvent: BTN_EXTRA"

    def test_format_wheel_event(self) -> None:
        """Test formatting wheel event."""
        app = Application(app_name="VSCode")
        window = Window(title="main.py")
        window_info = WindowInfo(application=app, window=window)
        event = MouseEvent.wheel_event(WheelAxis.REL_HWHEEL, 1)
        context = DispatchContext(event=event, window_info=window_info)

        result = format_dispatch_context(context)

        assert result == "Application: VSCode\nTitle: main.py\nEvent: REL_HWHEEL"

    def test_format_button_event_no_button(self) -> None:
        """Test formatting button event with no button (edge case)."""
        event = MouseEvent(event_type=EventType.BUTTON, button=None, value=1)
        context = DispatchContext(event=event, window_info=None)

        result = format_dispatch_context(context)

        assert result == "Application: Unknown\nTitle: Unknown\nEvent: Unknown"

    def test_format_wheel_event_no_wheel(self) -> None:
        """Test formatting wheel event with no wheel (edge case)."""
        event = MouseEvent(event_type=EventType.WHEEL, wheel=None, value=1)
        context = DispatchContext(event=event, window_info=None)

        result = format_dispatch_context(context)

        assert result == "Application: Unknown\nTitle: Unknown\nEvent: Unknown"
