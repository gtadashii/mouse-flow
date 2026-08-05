from __future__ import annotations

from pathlib import Path

import pytest

from mouseflow.domain import (
    GLOBAL_PROFILE_NAME,
    ActionType,
    Configuration,
    InputIdentifier,
)
from mouseflow.parser import (
    ConfigurationError,
    ValidationError,
    parse_config,
)


class TestParseConfig:
    def test_parse_valid_config(self, tmp_path: Path) -> None:
        """Test parsing a valid YAML configuration file."""
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
        assert config.profiles[0].app_name == "firefox"
        assert InputIdentifier.BTN_SIDE in config.profiles[0].mappings

    def test_parse_missing_config_file(self, tmp_path: Path) -> None:
        """Test parsing when configuration file does not exist."""
        config_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(ConfigurationError, match="not found"):
            parse_config(config_file)

    def test_parse_empty_config_file(self, tmp_path: Path) -> None:
        """Test parsing an empty configuration file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        with pytest.raises(ValidationError, match="Missing required field"):
            parse_config(config_file)


class TestValidateConfig:
    def test_validate_valid_structure(self, tmp_path: Path) -> None:
        """Test validation of a valid configuration structure."""
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

        assert config is not None

    def test_validate_invalid_action_type(self, tmp_path: Path) -> None:
        """Test validation rejects unrecognized action type."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: invalid_type\n"
            "        payload: alt+left\n",
        )

        with pytest.raises(ValidationError, match="invalid action type"):
            parse_config(config_file)

    def test_validate_missing_app_name(self, tmp_path: Path) -> None:
        """Test validation rejects profile missing app_name."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n",
        )

        with pytest.raises(ValidationError, match="app_name"):
            parse_config(config_file)

    def test_validate_missing_mappings(self, tmp_path: Path) -> None:
        """Test validation rejects profile missing mappings."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n  - app_name: firefox\n",
        )

        with pytest.raises(ValidationError, match="mappings"):
            parse_config(config_file)

    def test_validate_missing_profiles_key(self, tmp_path: Path) -> None:
        """Test validation rejects config without profiles key."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("foo: bar\n")

        with pytest.raises(ValidationError, match="profiles"):
            parse_config(config_file)

    def test_validate_invalid_mapping_format(self, tmp_path: Path) -> None:
        """Test validation rejects mapping with missing type field."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        payload: alt+left\n",
        )

        with pytest.raises(ValidationError, match="type"):
            parse_config(config_file)

    def test_validate_invalid_mapping_missing_payload(self, tmp_path: Path) -> None:
        """Test validation rejects mapping with missing payload field."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n",
        )

        with pytest.raises(ValidationError, match="payload"):
            parse_config(config_file)


class TestTranslateConfig:
    def test_translate_to_configuration(self, tmp_path: Path) -> None:
        """Test translating configuration to Configuration domain object."""
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

        assert isinstance(config, Configuration)
        assert len(config.profiles) == 1
        assert config.profiles[0].app_name == "firefox"

    def test_translate_keyboard_action(self, tmp_path: Path) -> None:
        """Test translating keyboard action mapping."""
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
        action = config.profiles[0].mappings[InputIdentifier.BTN_SIDE]

        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"

    def test_translate_command_action(self, tmp_path: Path) -> None:
        """Test translating command action mapping."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_EXTRA:\n"
            "        type: command\n"
            "        payload: swaymsg workspace 1\n",
        )

        config = parse_config(config_file)
        action = config.profiles[0].mappings[InputIdentifier.BTN_EXTRA]

        assert action.action_type == ActionType.COMMAND
        assert action.payload == "swaymsg workspace 1"

    def test_translate_multiple_profiles(self, tmp_path: Path) -> None:
        """Test translating multiple profiles."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n"
            "  - app_name: vscode\n"
            "    mappings:\n"
            "      BTN_EXTRA:\n"
            "        type: keyboard\n"
            "        payload: ctrl+shift+p\n",
        )

        config = parse_config(config_file)

        assert len(config.profiles) == 2
        assert config.profiles[0].app_name == "firefox"
        assert config.profiles[1].app_name == "vscode"


class TestGlobalProfileParsing:
    def test_parse_global_profile(self, tmp_path: Path) -> None:
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

        global_profile = config.get_global_profile()
        assert global_profile is not None
        assert global_profile.app_name == GLOBAL_PROFILE_NAME
        assert InputIdentifier.BTN_SIDE in global_profile.mappings

    def test_parse_global_profile_only(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n  BTN_SIDE:\n    type: keyboard\n    payload: alt+left\n",
        )

        config = parse_config(config_file)

        assert len(config.profiles) == 1
        assert config.profiles[0].app_name == GLOBAL_PROFILE_NAME

    def test_parse_backward_compatibility_no_global(self, tmp_path: Path) -> None:
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
        assert config.profiles[0].app_name == "firefox"
        assert config.get_global_profile() is None

    def test_validate_global_profile_name_collision(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: global\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: alt+left\n",
        )

        with pytest.raises(ValidationError, match="reserved name"):
            parse_config(config_file)

    def test_parse_global_profile_with_command(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n"
            "  BTN_EXTRA:\n"
            "    type: command\n"
            "    payload: swaymsg workspace next\n",
        )

        config = parse_config(config_file)

        global_profile = config.get_global_profile()
        assert global_profile is not None
        action = global_profile.mappings[InputIdentifier.BTN_EXTRA]
        assert action.action_type == ActionType.COMMAND
        assert action.payload == "swaymsg workspace next"

    def test_parse_global_and_application_profiles(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n"
            "  BTN_SIDE:\n"
            "    type: keyboard\n"
            "    payload: alt+left\n"
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      BTN_SIDE:\n"
            "        type: keyboard\n"
            "        payload: ctrl+left\n"
            "  - app_name: vscode\n"
            "    mappings:\n"
            "      BTN_EXTRA:\n"
            "        type: keyboard\n"
            "        payload: ctrl+shift+p\n",
        )

        config = parse_config(config_file)

        assert len(config.profiles) == 3
        global_profile = config.get_global_profile()
        assert global_profile is not None
        firefox_profile = config.get_profile("firefox")
        assert firefox_profile is not None
        vscode_profile = config.get_profile("vscode")
        assert vscode_profile is not None


class TestThumbWheelParsing:
    def test_parse_thumb_wheel_mappings(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "profiles:\n"
            "  - app_name: firefox\n"
            "    mappings:\n"
            "      THUMB_WHEEL_LEFT:\n"
            "        type: keyboard\n"
            "        payload: ctrl+shift+tab\n"
            "      THUMB_WHEEL_RIGHT:\n"
            "        type: keyboard\n"
            "        payload: ctrl+tab\n",
        )

        config = parse_config(config_file)

        assert len(config.profiles) == 1
        profile = config.profiles[0]
        assert InputIdentifier.THUMB_WHEEL_LEFT in profile.mappings
        assert InputIdentifier.THUMB_WHEEL_RIGHT in profile.mappings
        left_action = profile.mappings[InputIdentifier.THUMB_WHEEL_LEFT]
        right_action = profile.mappings[InputIdentifier.THUMB_WHEEL_RIGHT]
        assert left_action.payload == "ctrl+shift+tab"
        assert right_action.payload == "ctrl+tab"

    def test_parse_thumb_wheel_in_global_profile(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            "global:\n"
            "  THUMB_WHEEL_LEFT:\n"
            "    type: keyboard\n"
            "    payload: alt+left\n"
            "  THUMB_WHEEL_RIGHT:\n"
            "    type: keyboard\n"
            "    payload: alt+right\n",
        )

        config = parse_config(config_file)

        global_profile = config.get_global_profile()
        assert global_profile is not None
        assert InputIdentifier.THUMB_WHEEL_LEFT in global_profile.mappings
        assert InputIdentifier.THUMB_WHEEL_RIGHT in global_profile.mappings
