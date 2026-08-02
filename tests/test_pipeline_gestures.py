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
    Gesture,
    GestureDirection,
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
        # Setup mock device
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        # Simulate gesture: BTN_EXTRA press, movement right, BTN_EXTRA release
        events_input = []

        # BTN_EXTRA press
        press_event = MagicMock()
        press_event.type = ecodes.EV_KEY
        press_event.code = ecodes.BTN_EXTRA
        press_event.value = 1
        events_input.append(press_event)

        # Movement right (100 pixels)
        for _ in range(10):
            move_event = MagicMock()
            move_event.type = ecodes.EV_REL
            move_event.code = ecodes.REL_X
            move_event.value = 10
            events_input.append(move_event)

        # BTN_EXTRA release
        release_event = MagicMock()
        release_event.type = ecodes.EV_KEY
        release_event.code = ecodes.BTN_EXTRA
        release_event.value = 0
        events_input.append(release_event)

        mock_device.read_loop.return_value = events_input

        # Setup configuration with gesture mapping
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={},
                    gesture_mappings={
                        GestureDirection.RIGHT: Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+right",
                        ),
                    },
                ),
            ),
        )

        # Mock window resolver
        mock_resolver = MagicMock(spec=SwayResolver)
        mock_resolver.resolve.return_value = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )

        # Process through pipeline
        dispatcher = EventDispatcher(mock_resolver)
        profile_resolver = DefaultProfileResolver()

        contexts = list(
            dispatcher.dispatch(read_events_with_gestures("/dev/input/event0"))
        )

        assert len(contexts) == 1
        context = contexts[0]

        # Verify gesture was recognized
        assert isinstance(context.event, Gesture)
        assert context.event.direction == GestureDirection.RIGHT

        # Verify profile resolution
        profile = profile_resolver.resolve(config, context.window_info)
        assert profile is not None
        assert profile.app_name == "firefox"

        # Verify action resolution
        action = resolve_action(context, profile)
        assert action is not None
        assert action.payload == "alt+right"

    @patch("mouseflow.engine.open_device")
    def test_gesture_with_global_profile_fallback(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test gesture with global profile fallback."""
        # Setup mock device
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        # Simulate gesture: BTN_EXTRA press, movement up, BTN_EXTRA release
        events_input = []

        # BTN_EXTRA press
        press_event = MagicMock()
        press_event.type = ecodes.EV_KEY
        press_event.code = ecodes.BTN_EXTRA
        press_event.value = 1
        events_input.append(press_event)

        # Movement up (100 pixels)
        for _ in range(10):
            move_event = MagicMock()
            move_event.type = ecodes.EV_REL
            move_event.code = ecodes.REL_Y
            move_event.value = -10
            events_input.append(move_event)

        # BTN_EXTRA release
        release_event = MagicMock()
        release_event.type = ecodes.EV_KEY
        release_event.code = ecodes.BTN_EXTRA
        release_event.value = 0
        events_input.append(release_event)

        mock_device.read_loop.return_value = events_input

        # Setup configuration with global gesture mapping
        config = Configuration(
            profiles=(
                Profile(
                    app_name="global",
                    mappings={},
                    gesture_mappings={
                        GestureDirection.UP: Action(
                            action_type=ActionType.COMMAND,
                            payload="swaymsg workspace next",
                        ),
                    },
                ),
            ),
        )

        # Mock window resolver (app not in config, should use global)
        mock_resolver = MagicMock(spec=SwayResolver)
        mock_resolver.resolve.return_value = WindowInfo(
            application=Application(app_name="unknown_app"),
            window=Window(title="Test"),
        )

        # Process through pipeline
        dispatcher = EventDispatcher(mock_resolver)
        profile_resolver = DefaultProfileResolver()

        contexts = list(
            dispatcher.dispatch(read_events_with_gestures("/dev/input/event0"))
        )

        assert len(contexts) == 1
        context = contexts[0]

        # Verify gesture was recognized
        assert isinstance(context.event, Gesture)
        assert context.event.direction == GestureDirection.UP

        # Verify global profile resolution
        profile = profile_resolver.resolve(config, context.window_info)
        assert profile is not None
        assert profile.app_name == "global"

        # Verify action resolution
        action = resolve_action(context, profile)
        assert action is not None
        assert action.payload == "swaymsg workspace next"

    @patch("mouseflow.engine.open_device")
    def test_gesture_with_application_specific_profile(
        self,
        mock_open_device: MagicMock,
    ) -> None:
        """Test gesture with application-specific profile."""
        # Setup mock device
        mock_device = MagicMock()
        mock_open_device.return_value = mock_device

        # Simulate gesture: BTN_EXTRA press, movement left, BTN_EXTRA release
        events_input = []

        # BTN_EXTRA press
        press_event = MagicMock()
        press_event.type = ecodes.EV_KEY
        press_event.code = ecodes.BTN_EXTRA
        press_event.value = 1
        events_input.append(press_event)

        # Movement left (100 pixels)
        for _ in range(10):
            move_event = MagicMock()
            move_event.type = ecodes.EV_REL
            move_event.code = ecodes.REL_X
            move_event.value = -10
            events_input.append(move_event)

        # BTN_EXTRA release
        release_event = MagicMock()
        release_event.type = ecodes.EV_KEY
        release_event.code = ecodes.BTN_EXTRA
        release_event.value = 0
        events_input.append(release_event)

        mock_device.read_loop.return_value = events_input

        # Setup configuration with app-specific and global gesture mappings
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={},
                    gesture_mappings={
                        GestureDirection.LEFT: Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                    },
                ),
                Profile(
                    app_name="global",
                    mappings={},
                    gesture_mappings={
                        GestureDirection.LEFT: Action(
                            action_type=ActionType.KEYBOARD,
                            payload="ctrl+left",
                        ),
                    },
                ),
            ),
        )

        # Mock window resolver
        mock_resolver = MagicMock(spec=SwayResolver)
        mock_resolver.resolve.return_value = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )

        # Process through pipeline
        dispatcher = EventDispatcher(mock_resolver)
        profile_resolver = DefaultProfileResolver()

        contexts = list(
            dispatcher.dispatch(read_events_with_gestures("/dev/input/event0"))
        )

        assert len(contexts) == 1
        context = contexts[0]

        # Verify gesture was recognized
        assert isinstance(context.event, Gesture)
        assert context.event.direction == GestureDirection.LEFT

        # Verify app-specific profile resolution (not global)
        profile = profile_resolver.resolve(config, context.window_info)
        assert profile is not None
        assert profile.app_name == "firefox"

        # Verify action resolution (app-specific, not global)
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

        # Verify gesture mappings were loaded
        profile = config.profiles[0]
        assert GestureDirection.LEFT in profile.gesture_mappings
        assert GestureDirection.RIGHT in profile.gesture_mappings

        # Verify action resolution
        gesture = Gesture(direction=GestureDirection.LEFT)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        from mouseflow.domain import DispatchContext

        context = DispatchContext(event=gesture, window_info=window_info)
        action = resolve_action(context, profile)

        assert action is not None
        assert action.payload == "alt+left"
