from __future__ import annotations

from pathlib import Path

from mouseflow.domain import (
    Action,
    ActionType,
    Application,
    Configuration,
    DispatchContext,
    MouseButton,
    MouseEvent,
    Profile,
    WheelAxis,
    Window,
    WindowInfo,
)
from mouseflow.loader import resolve_action


class TestResolveAction:
    def test_resolve_matching_rule_exists(self) -> None:
        """Test resolving action when matching rule exists."""
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                    },
                ),
            ),
        )
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)

        assert action is not None
        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"

    def test_resolve_no_profile_for_application(self) -> None:
        """Test resolving when no profile exists for application."""
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                    },
                ),
            ),
        )
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="chrome"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)

        assert action is None

    def test_resolve_no_mapping_for_event(self) -> None:
        """Test resolving when no mapping exists for event."""
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                    },
                ),
            ),
        )
        event = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)

        assert action is None

    def test_resolve_null_window_info(self) -> None:
        """Test resolving when WindowInfo is null."""
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                    },
                ),
            ),
        )
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        context = DispatchContext(event=event, window_info=None)

        action = resolve_action(context, config)

        assert action is None

    def test_resolve_wheel_event(self) -> None:
        """Test resolving wheel event."""
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "REL_HWHEEL": Action(
                            action_type=ActionType.COMMAND,
                            payload="swaymsg workspace next",
                        ),
                    },
                ),
            ),
        )
        event = MouseEvent.wheel_event(WheelAxis.REL_HWHEEL, 1)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)

        assert action is not None
        assert action.action_type == ActionType.COMMAND
        assert action.payload == "swaymsg workspace next"


class TestIntegration:
    def test_full_pipeline_parse_and_resolve(self, tmp_path: Path) -> None:
        """Test full pipeline: parse config → resolve action."""
        from mouseflow.parser import parse_config

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n"
            "      BTN_EXTRA:\n"
            "        type: command\n"
            "        payload: swaymsg workspace 1\n",
        )

        config = parse_config(config_file)

        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)

        assert action is not None
        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"

    def test_full_pipeline_no_match(self, tmp_path: Path) -> None:
        """Test full pipeline when no action matches."""
        from mouseflow.parser import parse_config

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

        event = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        window_info = WindowInfo(
            application=Application(app_name="chrome"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)

        assert action is None
