"""Tests for configuration parser and loader gesture support."""

from pathlib import Path

import pytest

from mouseflow.domain import (
    Action,
    ActionType,
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
from mouseflow.loader import resolve_action
from mouseflow.parser import (
    ValidationError,
    parse_config,
)


class TestParseGestures:
    def test_parse_profile_with_gestures(self, tmp_path: Path) -> None:
        """Test parsing a profile with gesture mappings."""
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

        assert len(config.profiles) == 1
        profile = config.profiles[0]
        assert profile.app_name == "firefox"
        assert GestureDirection.LEFT in profile.gesture_mappings
        assert GestureDirection.RIGHT in profile.gesture_mappings
        assert profile.gesture_mappings[GestureDirection.LEFT].payload == "alt+left"
        assert profile.gesture_mappings[GestureDirection.RIGHT].payload == "alt+right"

    def test_parse_global_gestures(self, tmp_path: Path) -> None:
        """Test parsing global gesture mappings."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n"
            "  BTN_SIDE:\n"
            "    type: keyboard\n"
            "    payload: alt+left\n"
            "global_gestures:\n"
            "  UP:\n"
            "    type: command\n"
            "    payload: swaymsg workspace next\n",
        )

        config = parse_config(config_file)

        assert len(config.profiles) == 1
        profile = config.profiles[0]
        assert profile.app_name == "global"
        assert GestureDirection.UP in profile.gesture_mappings
        assert (
            profile.gesture_mappings[GestureDirection.UP].payload
            == "swaymsg workspace next"
        )

    def test_parse_all_gesture_directions(self, tmp_path: Path) -> None:
        """Test parsing all gesture directions."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: test\n"
            "    mappings: {}\n"
            "    gestures:\n"
            "      UP:\n"
            "        type: keyboard\n"
            "        payload: up\n"
            "      DOWN:\n"
            "        type: keyboard\n"
            "        payload: down\n"
            "      LEFT:\n"
            "        type: keyboard\n"
            "        payload: left\n"
            "      RIGHT:\n"
            "        type: keyboard\n"
            "        payload: right\n",
        )

        config = parse_config(config_file)

        profile = config.profiles[0]
        assert len(profile.gesture_mappings) == 4
        assert GestureDirection.UP in profile.gesture_mappings
        assert GestureDirection.DOWN in profile.gesture_mappings
        assert GestureDirection.LEFT in profile.gesture_mappings
        assert GestureDirection.RIGHT in profile.gesture_mappings


class TestValidateGestures:
    def test_invalid_gesture_direction(self, tmp_path: Path) -> None:
        """Test that invalid gesture direction is rejected."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: test\n"
            "    mappings: {}\n"
            "    gestures:\n"
            "      INVALID:\n"
            "        type: keyboard\n"
            "        payload: test\n",
        )

        with pytest.raises(ValidationError, match=r"INVALID.*invalid"):
            parse_config(config_file)

    def test_gesture_missing_type(self, tmp_path: Path) -> None:
        """Test that gesture missing type field is rejected."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: test\n"
            "    mappings: {}\n"
            "    gestures:\n"
            "      LEFT:\n"
            "        payload: test\n",
        )

        with pytest.raises(ValidationError, match="missing required field: type"):
            parse_config(config_file)

    def test_gesture_missing_payload(self, tmp_path: Path) -> None:
        """Test that gesture missing payload field is rejected."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: test\n"
            "    mappings: {}\n"
            "    gestures:\n"
            "      LEFT:\n"
            "        type: keyboard\n",
        )

        with pytest.raises(ValidationError, match="missing required field: payload"):
            parse_config(config_file)

    def test_gesture_invalid_action_type(self, tmp_path: Path) -> None:
        """Test that gesture with invalid action type is rejected."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: test\n"
            "    mappings: {}\n"
            "    gestures:\n"
            "      LEFT:\n"
            "        type: invalid\n"
            "        payload: test\n",
        )

        with pytest.raises(ValidationError, match="invalid action type"):
            parse_config(config_file)


class TestResolveGestureActions:
    def test_resolve_gesture_action(self) -> None:
        """Test resolving action for a gesture event."""
        profile = Profile(
            app_name="firefox",
            mappings={},
            gesture_mappings={
                GestureDirection.LEFT: Action(
                    action_type=ActionType.KEYBOARD,
                    payload="alt+left",
                ),
            },
        )
        gesture = Gesture(direction=GestureDirection.LEFT)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=gesture, window_info=window_info)

        action = resolve_action(context, profile)

        assert action is not None
        assert action.payload == "alt+left"

    def test_resolve_gesture_no_mapping(self) -> None:
        """Test resolving gesture with no mapping returns None."""
        profile = Profile(
            app_name="firefox",
            mappings={},
            gesture_mappings={},
        )
        gesture = Gesture(direction=GestureDirection.LEFT)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=gesture, window_info=window_info)

        action = resolve_action(context, profile)

        assert action is None

    def test_resolve_gesture_with_global_profile(self) -> None:
        """Test resolving gesture with global profile."""
        profile = Profile(
            app_name="global",
            mappings={},
            gesture_mappings={
                GestureDirection.UP: Action(
                    action_type=ActionType.COMMAND,
                    payload="swaymsg workspace next",
                ),
            },
        )
        gesture = Gesture(direction=GestureDirection.UP)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=gesture, window_info=window_info)

        action = resolve_action(context, profile)

        assert action is not None
        assert action.payload == "swaymsg workspace next"

    def test_resolve_mouse_event_still_works(self) -> None:
        """Test that mouse event resolution still works."""
        profile = Profile(
            app_name="firefox",
            mappings={
                "BTN_SIDE": Action(
                    action_type=ActionType.KEYBOARD,
                    payload="alt+left",
                ),
            },
            gesture_mappings={},
        )
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, profile)

        assert action is not None
        assert action.payload == "alt+left"


class TestBackwardCompatibility:
    def test_config_without_gestures(self, tmp_path: Path) -> None:
        """Test that config without gestures section still works."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n",
        )

        config = parse_config(config_file)

        assert len(config.profiles) == 1
        profile = config.profiles[0]
        assert profile.app_name == "firefox"
        assert len(profile.gesture_mappings) == 0
        assert "BTN_SIDE" in profile.mappings

    def test_global_without_gestures(self, tmp_path: Path) -> None:
        """Test that global config without gestures still works."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n  BTN_SIDE:\n    type: keyboard\n    payload: alt+left\n",
        )

        config = parse_config(config_file)

        assert len(config.profiles) == 1
        profile = config.profiles[0]
        assert profile.app_name == "global"
        assert len(profile.gesture_mappings) == 0
