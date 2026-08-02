from __future__ import annotations

from pathlib import Path

from mouseflow.domain import (
    Action,
    ActionType,
    Application,
    DispatchContext,
    InputIdentifier,
    Profile,
    UserInput,
    Window,
    WindowInfo,
)
from mouseflow.loader import resolve_action
from mouseflow.profile_resolver import DefaultProfileResolver


class TestResolveAction:
    def test_resolve_matching_rule_exists(self) -> None:
        """Test resolving action when matching rule exists."""
        profile = Profile(
            app_name="firefox",
            mappings={
                InputIdentifier.BTN_SIDE: Action(
                    action_type=ActionType.KEYBOARD,
                    payload="alt+left",
                ),
            },
        )
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        context = DispatchContext(event=event)

        action = resolve_action(context, profile)

        assert action is not None
        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"

    def test_resolve_no_mapping_for_event(self) -> None:
        """Test resolving when no mapping exists for event."""
        profile = Profile(
            app_name="firefox",
            mappings={
                InputIdentifier.BTN_SIDE: Action(
                    action_type=ActionType.KEYBOARD,
                    payload="alt+left",
                ),
            },
        )
        event = UserInput(identifier=InputIdentifier.BTN_EXTRA)
        context = DispatchContext(event=event)

        action = resolve_action(context, profile)

        assert action is None

    def test_resolve_null_profile(self) -> None:
        """Test resolving when profile is null."""
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        context = DispatchContext(event=event)

        action = resolve_action(context, None)

        assert action is None

    def test_resolve_gesture_input(self) -> None:
        """Test resolving gesture input."""
        profile = Profile(
            app_name="firefox",
            mappings={
                InputIdentifier.GESTURE_RIGHT: Action(
                    action_type=ActionType.COMMAND,
                    payload="swaymsg workspace next",
                ),
            },
        )
        event = UserInput(identifier=InputIdentifier.GESTURE_RIGHT)
        context = DispatchContext(event=event)

        action = resolve_action(context, profile)

        assert action is not None
        assert action.action_type == ActionType.COMMAND
        assert action.payload == "swaymsg workspace next"


class TestIntegration:
    def test_full_pipeline_parse_and_resolve(self, tmp_path: Path) -> None:
        """Test full pipeline: parse config → resolve profile → resolve action."""
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
        resolver = DefaultProfileResolver()

        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        profile = resolver.resolve(config, window_info)
        action = resolve_action(context, profile)

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
        resolver = DefaultProfileResolver()

        event = UserInput(identifier=InputIdentifier.BTN_EXTRA)
        window_info = WindowInfo(
            application=Application(app_name="chrome"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        profile = resolver.resolve(config, window_info)
        action = resolve_action(context, profile)

        assert action is None

    def test_full_pipeline_with_global_fallback(self, tmp_path: Path) -> None:
        """Test full pipeline with global profile fallback."""
        from mouseflow.parser import parse_config

        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n"
            "  BTN_SIDE:\n"
            "    type: keyboard\n"
            "    payload: alt+left\n"
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_EXTRA:\n"
            "        type: keyboard\n"
            "        payload: alt+right\n",
        )

        config = parse_config(config_file)
        resolver = DefaultProfileResolver()

        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="chrome"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        profile = resolver.resolve(config, window_info)
        action = resolve_action(context, profile)

        assert action is not None
        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"
