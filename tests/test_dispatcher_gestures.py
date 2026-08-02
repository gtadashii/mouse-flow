"""Tests for event dispatcher gesture support."""

from mouseflow.dispatcher import EventDispatcher, format_dispatch_context
from mouseflow.domain import (
    Application,
    DispatchContext,
    InputIdentifier,
    Profile,
    UserInput,
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
    def test_dispatch_button_input(self) -> None:
        """Test dispatching a button input."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = MockWindowResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        events = [event]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert isinstance(contexts[0], DispatchContext)
        assert contexts[0].event == event
        assert contexts[0].window_info == window_info

    def test_dispatch_gesture_input(self) -> None:
        """Test dispatching a gesture input."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = MockWindowResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        event = UserInput(identifier=InputIdentifier.GESTURE_LEFT)
        events = [event]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert isinstance(contexts[0], DispatchContext)
        assert contexts[0].event == event
        assert contexts[0].window_info == window_info

    def test_dispatch_mixed_inputs(self) -> None:
        """Test dispatching both button and gesture inputs."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = MockWindowResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        button_input = UserInput(identifier=InputIdentifier.BTN_SIDE)
        gesture_input = UserInput(identifier=InputIdentifier.GESTURE_RIGHT)
        events: list[UserInput] = [button_input, gesture_input]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 2
        assert contexts[0].event == button_input
        assert contexts[1].event == gesture_input
        assert resolver.resolve_call_count == 2

    def test_dispatch_gesture_with_window_info(self) -> None:
        """Test that window info is queried for gesture inputs."""
        window_info = WindowInfo(
            application=Application(app_name="vscode"),
            window=Window(title="test.py"),
        )
        resolver = MockWindowResolver(window_info)
        dispatcher = EventDispatcher(resolver)

        event = UserInput(identifier=InputIdentifier.GESTURE_UP)
        events = [event]

        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 1
        assert contexts[0].window_info == window_info
        assert resolver.resolve_call_count == 1

    def test_dispatch_gesture_without_window_info(self) -> None:
        """Test dispatching gesture when window resolution fails."""
        resolver = MockWindowResolver(None)
        dispatcher = EventDispatcher(resolver)

        event = UserInput(identifier=InputIdentifier.GESTURE_DOWN)
        events = [event]

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
        event = UserInput(identifier=InputIdentifier.GESTURE_LEFT)
        context = DispatchContext(event=event, window_info=window_info)

        result = format_dispatch_context(context)

        assert "Application: firefox" in result
        assert "Title: ChatGPT" in result
        assert "Input: GESTURE_LEFT" in result

    def test_format_gesture_without_window_info(self) -> None:
        """Test formatting gesture context without window info."""
        event = UserInput(identifier=InputIdentifier.GESTURE_RIGHT)
        context = DispatchContext(event=event, window_info=None)

        result = format_dispatch_context(context)

        assert "Application: Unknown" in result
        assert "Title: Unknown" in result
        assert "Input: GESTURE_RIGHT" in result

    def test_format_gesture_with_profile(self) -> None:
        """Test formatting gesture context with profile."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        event = UserInput(identifier=InputIdentifier.GESTURE_UP)
        context = DispatchContext(event=event, window_info=window_info)
        profile = Profile(app_name="firefox")

        result = format_dispatch_context(context, profile)

        assert "Profile: firefox" in result

    def test_format_gesture_with_global_profile(self) -> None:
        """Test formatting gesture context with global profile."""
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        event = UserInput(identifier=InputIdentifier.GESTURE_DOWN)
        context = DispatchContext(event=event, window_info=window_info)
        profile = Profile(app_name="global")

        result = format_dispatch_context(context, profile)

        assert "Profile: global" in result

    def test_format_all_gesture_directions(self) -> None:
        """Test formatting all gesture directions."""
        window_info = WindowInfo(
            application=Application(app_name="test"),
            window=Window(title="Test"),
        )

        gesture_identifiers = [
            InputIdentifier.GESTURE_UP,
            InputIdentifier.GESTURE_DOWN,
            InputIdentifier.GESTURE_LEFT,
            InputIdentifier.GESTURE_RIGHT,
        ]

        for identifier in gesture_identifiers:
            event = UserInput(identifier=identifier)
            context = DispatchContext(event=event, window_info=window_info)

            result = format_dispatch_context(context)

            assert f"Input: {identifier.value}" in result
