from __future__ import annotations

from collections.abc import Iterable

from mouseflow.dispatcher import EventDispatcher, format_dispatch_context
from mouseflow.domain import (
    GLOBAL_PROFILE_NAME,
    Application,
    DispatchContext,
    InputIdentifier,
    Profile,
    UserInput,
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

        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
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

        event = UserInput(identifier=InputIdentifier.BTN_EXTRA)
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

        event1 = UserInput(identifier=InputIdentifier.BTN_SIDE)
        event2 = UserInput(identifier=InputIdentifier.BTN_EXTRA)
        event3 = UserInput(identifier=InputIdentifier.GESTURE_RIGHT)
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

        events: Iterable[UserInput] = iter([])
        contexts = list(dispatcher.dispatch(events))

        assert len(contexts) == 0
        assert resolver.resolve_call_count == 0

    def test_dispatch_independence(self) -> None:
        """Test that each event is processed independently."""
        resolver = MockResolver()
        dispatcher = EventDispatcher(resolver)

        event1 = UserInput(identifier=InputIdentifier.BTN_SIDE)
        event2 = UserInput(identifier=InputIdentifier.BTN_EXTRA)
        events = iter([event1, event2])

        contexts = list(dispatcher.dispatch(events))

        assert contexts[0].event == event1
        assert contexts[1].event == event2
        assert contexts[0] != contexts[1]


class TestFormatDispatchContext:
    def test_format_with_window_info(self) -> None:
        """Test formatting with window info."""
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        window_info = WindowInfo(application=app, window=window)
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        context = DispatchContext(event=event, window_info=window_info)

        result = format_dispatch_context(context)

        assert result == "Application: Firefox\nTitle: ChatGPT\nInput: BTN_SIDE"

    def test_format_without_window_info(self) -> None:
        """Test formatting without window info."""
        event = UserInput(identifier=InputIdentifier.BTN_EXTRA)
        context = DispatchContext(event=event, window_info=None)

        result = format_dispatch_context(context)

        assert result == "Application: Unknown\nTitle: Unknown\nInput: BTN_EXTRA"

    def test_format_gesture_input(self) -> None:
        """Test formatting gesture input."""
        app = Application(app_name="VSCode")
        window = Window(title="main.py")
        window_info = WindowInfo(application=app, window=window)
        event = UserInput(identifier=InputIdentifier.GESTURE_RIGHT)
        context = DispatchContext(event=event, window_info=window_info)

        result = format_dispatch_context(context)

        assert result == "Application: VSCode\nTitle: main.py\nInput: GESTURE_RIGHT"

    def test_format_with_application_profile(self) -> None:
        """Test formatting with application-specific profile."""
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        window_info = WindowInfo(application=app, window=window)
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        context = DispatchContext(event=event, window_info=window_info)
        profile = Profile(app_name="firefox", mappings={})

        result = format_dispatch_context(context, profile)

        assert "Application: Firefox" in result
        assert "Title: ChatGPT" in result
        assert "Input: BTN_SIDE" in result
        assert "Profile: firefox" in result

    def test_format_with_global_profile(self) -> None:
        """Test formatting with global profile."""
        app = Application(app_name="Chrome")
        window = Window(title="Test")
        window_info = WindowInfo(application=app, window=window)
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        context = DispatchContext(event=event, window_info=window_info)
        profile = Profile(app_name=GLOBAL_PROFILE_NAME, mappings={})

        result = format_dispatch_context(context, profile)

        assert "Application: Chrome" in result
        assert "Profile: global" in result

    def test_format_without_profile(self) -> None:
        """Test formatting without profile (backward compatibility)."""
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        window_info = WindowInfo(application=app, window=window)
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        context = DispatchContext(event=event, window_info=window_info)

        result = format_dispatch_context(context)

        assert "Profile:" not in result
