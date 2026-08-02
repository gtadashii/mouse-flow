"""Integration tests for complete gesture pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from evdev import ecodes

from mouseflow.dispatcher import EventDispatcher
from mouseflow.domain import (
    Action,
    ActionType,
    Application,
    Configuration,
    InputIdentifier,
    Profile,
    Window,
    WindowInfo,
)
from mouseflow.engine import read_events_with_gestures
from mouseflow.loader import resolve_action
from mouseflow.parser import parse_config
from mouseflow.profile_resolver import DefaultProfileResolver
from mouseflow.resolver import SwayResolver


class TestGesturePipelineIntegration:
    @patch("mouseflow.engine.open_device")
    def test_complete_gesture_flow(self, mock_open_device: MagicMock) -> None:
        """Test complete gesture flow from input to action resolution."""
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

        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        InputIdentifier.GESTURE_RIGHT: Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+right",
                        ),
                    },
                ),
            ),
        )

        mock_resolver = MagicMock(spec=SwayResolver)
        mock_resolver.resolve.return_value = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )

        dispatcher = EventDispatcher(mock_resolver)
        profile_resolver = DefaultProfileResolver()

        contexts = list(
            dispatcher.dispatch(read_events_with_gestures("/dev/input/event0"))
        )

        assert len(contexts) == 1
        context = contexts[0]

        assert context.event.identifier == InputIdentifier.GESTURE_RIGHT

        profile = profile_resolver.resolve(config, context.window_info)
        assert profile is not None
        assert profile.app_name == "firefox"

        action = resolve_action(context, profile)
        assert action is not None
        assert action.payload == "alt+right"

    @patch("mouseflow.engine.open_device")
    def test_gesture_with_global_profile_fallback(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test gesture with global profile fallback."""
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
            move_event.code = ecodes.REL_Y
            move_event.value = -10
            events_input.append(move_event)

        release_event = MagicMock()
        release_event.type = ecodes.EV_KEY
        release_event.code = ecodes.BTN_EXTRA
        release_event.value = 0
        events_input.append(release_event)

        mock_device.read_loop.return_value = events_input

        config = Configuration(
            profiles=(
                Profile(
                    app_name="global",
                    mappings={
                        InputIdentifier.GESTURE_UP: Action(
                            action_type=ActionType.COMMAND,
                            payload="swaymsg workspace next",
                        ),
                    },
                ),
            ),
        )

        mock_resolver = MagicMock(spec=SwayResolver)
        mock_resolver.resolve.return_value = WindowInfo(
            application=Application(app_name="unknown_app"),
            window=Window(title="Test"),
        )

        dispatcher = EventDispatcher(mock_resolver)
        profile_resolver = DefaultProfileResolver()

        contexts = list(
            dispatcher.dispatch(read_events_with_gestures("/dev/input/event0"))
        )

        assert len(contexts) == 1
        context = contexts[0]

        assert context.event.identifier == InputIdentifier.GESTURE_UP

        profile = profile_resolver.resolve(config, context.window_info)
        assert profile is not None
        assert profile.app_name == "global"

        action = resolve_action(context, profile)
        assert action is not None
        assert action.payload == "swaymsg workspace next"

    @patch("mouseflow.engine.open_device")
    def test_gesture_with_application_specific_profile(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test gesture with application-specific profile."""
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
            move_event.value = -10
            events_input.append(move_event)

        release_event = MagicMock()
        release_event.type = ecodes.EV_KEY
        release_event.code = ecodes.BTN_EXTRA
        release_event.value = 0
        events_input.append(release_event)

        mock_device.read_loop.return_value = events_input

        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        InputIdentifier.GESTURE_LEFT: Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                    },
                ),
                Profile(
                    app_name="global",
                    mappings={
                        InputIdentifier.GESTURE_LEFT: Action(
                            action_type=ActionType.KEYBOARD,
                            payload="ctrl+left",
                        ),
                    },
                ),
            ),
        )

        mock_resolver = MagicMock(spec=SwayResolver)
        mock_resolver.resolve.return_value = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )

        dispatcher = EventDispatcher(mock_resolver)
        profile_resolver = DefaultProfileResolver()

        contexts = list(
            dispatcher.dispatch(read_events_with_gestures("/dev/input/event0"))
        )

        assert len(contexts) == 1
        context = contexts[0]

        assert context.event.identifier == InputIdentifier.GESTURE_LEFT

        profile = profile_resolver.resolve(config, context.window_info)
        assert profile is not None
        assert profile.app_name == "firefox"

        action = resolve_action(context, profile)
        assert action is not None
        assert action.payload == "alt+left"

    def test_config_file_with_gestures(self, tmp_path: Path) -> None:
        """Test loading config file with gestures and resolving actions."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n"
            "    gestures:\n"
            "      LEFT:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n"
            "      RIGHT:\n"
            "        type: keyboard\n"
            "        payload: alt+right\n",
        )

        config = parse_config(config_file)

        profile = config.profiles[0]
        assert InputIdentifier.GESTURE_LEFT in profile.mappings
        assert InputIdentifier.GESTURE_RIGHT in profile.mappings

        from mouseflow.domain import DispatchContext, UserInput

        event = UserInput(identifier=InputIdentifier.GESTURE_LEFT)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )

        context = DispatchContext(event=event, window_info=window_info)
        action = resolve_action(context, profile)

        assert action is not None
        assert action.payload == "alt+left"
