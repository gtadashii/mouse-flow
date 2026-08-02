"""Tests for event dispatcher gesture support."""

from mouseflow.dispatcher import EventDispatcher, format_dispatch_context
from mouseflow.domain import (
    Application,
    DispatchContext,
    Gesture,
    GestureDirection,
    MouseButton,
    MouseEvent,
    Profile,
    Window,
    WindowInfo,
)


class MockWindowResolver:
    """Mock WindowResolver for testing."""

    def __init__(self, window_info: WindowInfo | None = None) -> None:
        self._window_info = window_info
        self.resolve_call_count = 0

    def resolve(self) -> WindowInfo | None:
        self.resolve_call_count += 1
        return self._window_info


class TestEventDispatcherWithGestures:
    def test_dispatch_mouse_event(self) -> None:
        """Test dispatching a mouse event."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = MockWindowResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        events = [event]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert isinstance(contexts[0], DispatchContext)
        assert contexts[0].event == event
        assert contexts[0].window_info == window_info

    def test_dispatch_gesture_event(self) -> None:
        """Test dispatching a gesture event."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = MockWindowResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        gesture = Gesture(direction=GestureDirection.LEFT)
        events = [gesture]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert isinstance(contexts[0], DispatchContext)
        assert contexts[0].event == gesture
        assert contexts[0].window_info == window_info

    def test_dispatch_mixed_events(self) -> None:
        """Test dispatching both mouse and gesture events."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = MockWindowResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        mouse_event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        gesture_event = Gesture(direction=GestureDirection.RIGHT)
        events: list[MouseEvent | Gesture] = [mouse_event, gesture_event]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 2
        assert contexts[0].event == mouse_event
        assert contexts[1].event == gesture_event
        assert resolver.resolve_call_count == 2

    def test_dispatch_gesture_with_window_info(self) -> None:
        """Test that window info is queried for gesture events."""
        window_info = WindowInfo(
            application=Application(app_name="vscode"),
            window=Window(title="test.py"),
        )
        resolver = MockWindowResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        gesture = Gesture(direction=GestureDirection.UP)
        events = [gesture]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert contexts[0].window_info == window_info
        assert resolver.resolve_call_count == 1

    def test_dispatch_gesture_without_window_info(self) -> None:
        """Test dispatching gesture when window resolution fails."""
        resolver = MockWindowResolver(None)
        dispatcher = EventDispatcher(resolver)

        gesture = Gesture(direction=GestureDirection.DOWN)
        events = [gesture]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert contexts[0].window_info is None


class TestFormatGestureContext:
    def test_format_gesture_with_window_info(self) -> None:
        """Test formatting gesture context with window info."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="ChatGPT"),
        )
        gesture = Gesture(direction=GestureDirection.LEFT)
        context = DispatchContext(event=gesture, window_info=window_info)

        result = format_dispatch_context(context)

        assert "Application: firefox" in result
        assert "Title: ChatGPT" in result
        assert "Gesture: LEFT" in result

    def test_format_gesture_without_window_info(self) -> None:
        """Test formatting gesture context without window info."""
        gesture = Gesture(direction=GestureDirection.RIGHT)
        context = DispatchContext(event=gesture, window_info=None)

        result = format_dispatch_context(context)

        assert "Application: Unknown" in result
        assert "Title: Unknown" in result
        assert "Gesture: RIGHT" in result

    def test_format_gesture_with_profile(self) -> None:
        """Test formatting gesture context with profile."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        gesture = Gesture(direction=GestureDirection.UP)
        context = DispatchContext(event=gesture, window_info=window_info)
        profile = Profile(app_name="firefox")

        result = format_dispatch_context(context, profile)

        assert "Profile: firefox" in result

    def test_format_gesture_with_global_profile(self) -> None:
        """Test formatting gesture context with global profile."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        gesture = Gesture(direction=GestureDirection.DOWN)
        context = DispatchContext(event=gesture, window_info=window_info)
        profile = Profile(app_name="global")

        result = format_dispatch_context(context, profile)

        assert "Profile: global" in result

    def test_format_all_gesture_directions(self) -> None:
        """Test formatting all gesture directions."""
        window_info = WindowInfo(
            application=Application(app_name="test"),
            window=Window(title="Test"),
        )

        for direction in GestureDirection:
            gesture = Gesture(direction=direction)
            context = DispatchContext(event=gesture, window_info=window_info)

            result = format_dispatch_context(context)

            assert f"Gesture: {direction.value}" in result
