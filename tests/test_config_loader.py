from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mouseflow.config_loader import (
    ConfigurationError,
    ValidationError,
    load_config,
    resolve_action,
    translate_config,
    validate_config,
)
from mouseflow.domain import (
    Action,
    ActionType,
    Application,
    DispatchContext,
    MouseButton,
    MouseEvent,
    Profile,
    WheelAxis,
    Window,
    WindowInfo,
)


class TestLoadConfig:
    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Test loading a valid YAML configuration file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n",
        )

        raw_config = load_config(config_file)

        assert "profiles" in raw_config
        assert len(raw_config["profiles"]) == 1
        assert raw_config["profiles"][0]["app_name"] == "firefox"

    def test_load_missing_config_file(self, tmp_path: Path) -> None:
        """Test loading when configuration file does not exist."""
        config_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(ConfigurationError, match="not found"):
            load_config(config_file)

    def test_load_empty_config_file(self, tmp_path: Path) -> None:
        """Test loading an empty configuration file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        with pytest.raises(ConfigurationError, match="empty"):
            load_config(config_file)


class TestValidateConfig:
    def test_validate_valid_structure(self) -> None:
        """Test validation of a valid configuration structure."""
        raw_config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_SIDE": {"type": "keyboard", "payload": "alt+left"},
                    },
                },
            ],
        }

        validate_config(raw_config)

    def test_validate_invalid_action_type(self) -> None:
        """Test validation rejects unrecognized action type."""
        raw_config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_SIDE": {"type": "invalid_type", "payload": "alt+left"},
                    },
                },
            ],
        }

        with pytest.raises(ValidationError, match="invalid action type"):
            validate_config(raw_config)

    def test_validate_missing_app_name(self) -> None:
        """Test validation rejects profile missing app_name."""
        raw_config = {
            "profiles": [
                {
                    "mappings": {
                        "BTN_SIDE": {"type": "keyboard", "payload": "alt+left"},
                    },
                },
            ],
        }

        with pytest.raises(ValidationError, match="app_name"):
            validate_config(raw_config)

    def test_validate_missing_mappings(self) -> None:
        """Test validation rejects profile missing mappings."""
        raw_config = {
            "profiles": [
                {"app_name": "firefox"},
            ],
        }

        with pytest.raises(ValidationError, match="mappings"):
            validate_config(raw_config)

    def test_validate_missing_profiles_key(self) -> None:
        """Test validation rejects config without profiles key."""
        raw_config: dict[str, Any] = {}

        with pytest.raises(ValidationError, match="profiles"):
            validate_config(raw_config)

    def test_validate_invalid_mapping_format(self) -> None:
        """Test validation rejects mapping with missing type field."""
        raw_config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_SIDE": {"payload": "alt+left"},
                    },
                },
            ],
        }

        with pytest.raises(ValidationError, match="type"):
            validate_config(raw_config)

    def test_validate_invalid_mapping_missing_payload(self) -> None:
        """Test validation rejects mapping with missing payload field."""
        raw_config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_SIDE": {"type": "keyboard"},
                    },
                },
            ],
        }

        with pytest.raises(ValidationError, match="payload"):
            validate_config(raw_config)


class TestTranslateConfig:
    def test_translate_to_profile(self) -> None:
        """Test translating configuration to Profile domain objects."""
        raw_config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_SIDE": {"type": "keyboard", "payload": "alt+left"},
                    },
                },
            ],
        }

        profiles = translate_config(raw_config)

        assert len(profiles) == 1
        assert profiles[0].app_name == "firefox"
        assert "BTN_SIDE" in profiles[0].mappings

    def test_translate_keyboard_action(self) -> None:
        """Test translating keyboard action mapping."""
        raw_config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_SIDE": {"type": "keyboard", "payload": "alt+left"},
                    },
                },
            ],
        }

        profiles = translate_config(raw_config)
        action = profiles[0].mappings["BTN_SIDE"]

        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"

    def test_translate_command_action(self) -> None:
        """Test translating command action mapping."""
        raw_config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_EXTRA": {
                            "type": "command",
                            "payload": "swaymsg workspace 1",
                        },
                    },
                },
            ],
        }

        profiles = translate_config(raw_config)
        action = profiles[0].mappings["BTN_EXTRA"]

        assert action.action_type == ActionType.COMMAND
        assert action.payload == "swaymsg workspace 1"

    def test_translate_multiple_profiles(self) -> None:
        """Test translating multiple profiles."""
        raw_config = {
            "profiles": [
                {
                    "app_name": "firefox",
                    "mappings": {
                        "BTN_SIDE": {"type": "keyboard", "payload": "alt+left"},
                    },
                },
                {
                    "app_name": "vscode",
                    "mappings": {
                        "BTN_EXTRA": {"type": "keyboard", "payload": "ctrl+shift+p"},
                    },
                },
            ],
        }

        profiles = translate_config(raw_config)

        assert len(profiles) == 2
        assert profiles[0].app_name == "firefox"
        assert profiles[1].app_name == "vscode"


class TestResolveAction:
    def test_resolve_matching_rule_exists(self) -> None:
        """Test resolving action when matching rule exists."""
        profiles = [
            Profile(
                app_name="firefox",
                mappings={
                    "BTN_SIDE": Action(
                        action_type=ActionType.KEYBOARD,
                        payload="alt+left",
                    ),
                },
            ),
        ]
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, profiles)

        assert action is not None
        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"

    def test_resolve_no_profile_for_application(self) -> None:
        """Test resolving when no profile exists for application."""
        profiles = [
            Profile(
                app_name="firefox",
                mappings={
                    "BTN_SIDE": Action(
                        action_type=ActionType.KEYBOARD,
                        payload="alt+left",
                    ),
                },
            ),
        ]
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="chrome"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, profiles)

        assert action is None

    def test_resolve_no_mapping_for_event(self) -> None:
        """Test resolving when no mapping exists for event."""
        profiles = [
            Profile(
                app_name="firefox",
                mappings={
                    "BTN_SIDE": Action(
                        action_type=ActionType.KEYBOARD,
                        payload="alt+left",
                    ),
                },
            ),
        ]
        event = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, profiles)

        assert action is None

    def test_resolve_null_window_info(self) -> None:
        """Test resolving when WindowInfo is null."""
        profiles = [
            Profile(
                app_name="firefox",
                mappings={
                    "BTN_SIDE": Action(
                        action_type=ActionType.KEYBOARD,
                        payload="alt+left",
                    ),
                },
            ),
        ]
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        context = DispatchContext(event=event, window_info=None)

        action = resolve_action(context, profiles)

        assert action is None

    def test_resolve_wheel_event(self) -> None:
        """Test resolving wheel event."""
        profiles = [
            Profile(
                app_name="firefox",
                mappings={
                    "REL_HWHEEL": Action(
                        action_type=ActionType.COMMAND,
                        payload="swaymsg workspace next",
                    ),
                },
            ),
        ]
        event = MouseEvent.wheel_event(WheelAxis.REL_HWHEEL, 1)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, profiles)

        assert action is not None
        assert action.action_type == ActionType.COMMAND
        assert action.payload == "swaymsg workspace next"


class TestIntegration:
    def test_full_pipeline_load_and_resolve(self, tmp_path: Path) -> None:
        """Test full pipeline: load config → validate → translate → resolve."""
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

        raw_config = load_config(config_file)
        validate_config(raw_config)
        profiles = translate_config(raw_config)

        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, profiles)

        assert action is not None
        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"

    def test_full_pipeline_no_match(self, tmp_path: Path) -> None:
        """Test full pipeline when no action matches."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n",
        )

        raw_config = load_config(config_file)
        validate_config(raw_config)
        profiles = translate_config(raw_config)

        event = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        window_info = WindowInfo(
            application=Application(app_name="chrome"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, profiles)

        assert action is None
