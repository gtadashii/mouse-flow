from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mouseflow.domain import (
    GLOBAL_PROFILE_NAME,
    Action,
    ActionType,
    Configuration,
    Profile,
)

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "mouseflow" / "config.yaml"


class ConfigurationError(Exception):
    pass


class ValidationError(ConfigurationError):
    pass


def parse_config(path: Path | None = None) -> Configuration:
    if path is None:
        path = DEFAULT_CONFIG_PATH
    raw_data = _load_yaml(path)
    _validate_structure(raw_data)
    return _translate_to_domain(raw_data)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {path}")

    content = path.read_text()
    if not content.strip():
        raise ConfigurationError("Configuration file is empty")

    data = yaml.safe_load(content)
    if data is None:
        raise ConfigurationError("Configuration file is empty")

    if not isinstance(data, dict):
        raise ConfigurationError("Configuration file must contain a mapping")

    return data


def _validate_action_mapping(
    event_key: str,
    action: Any,
    context: str,
) -> None:
    if not isinstance(action, dict):
        raise ValidationError(f"Mapping {event_key} in {context} must be a mapping")

    if "type" not in action:
        raise ValidationError(
            f"Mapping {event_key} in {context} missing required field: type",
        )

    if "payload" not in action:
        raise ValidationError(
            f"Mapping {event_key} in {context} missing required field: payload",
        )

    action_type = action["type"]
    if action_type not in ("keyboard", "command"):
        raise ValidationError(
            f"Mapping {event_key} in {context} has invalid action type: {action_type}",
        )


def _validate_structure(data: dict[str, Any]) -> None:
    if "profiles" not in data and "global" not in data:
        raise ValidationError("Missing required field: profiles or global")

    if "profiles" in data:
        profiles = data["profiles"]
        if not isinstance(profiles, list):
            raise ValidationError("profiles must be a list")

        for i, profile in enumerate(profiles):
            if not isinstance(profile, dict):
                raise ValidationError(f"Profile {i} must be a mapping")

            if "app_name" not in profile:
                raise ValidationError(f"Profile {i} missing required field: app_name")

            app_name = profile["app_name"]
            if app_name == GLOBAL_PROFILE_NAME:
                raise ValidationError(
                    f"Profile {i} cannot use reserved name '{GLOBAL_PROFILE_NAME}'. "
                    "Use 'global:' key at top level instead.",
                )

            if "mappings" not in profile:
                raise ValidationError(f"Profile {i} missing required field: mappings")

            mappings = profile["mappings"]
            if not isinstance(mappings, dict):
                raise ValidationError(f"Profile {i} mappings must be a mapping")

            for event_key, action in mappings.items():
                _validate_action_mapping(event_key, action, f"profile {i}")

    if "global" in data:
        global_mappings = data["global"]
        if not isinstance(global_mappings, dict):
            raise ValidationError("global must be a mapping")

        for event_key, action in global_mappings.items():
            _validate_action_mapping(event_key, action, "global")


def _translate_to_domain(data: dict[str, Any]) -> Configuration:
    profiles: list[Profile] = []

    if "global" in data:
        global_mappings = _parse_mappings(data["global"])
        profiles.append(Profile(app_name=GLOBAL_PROFILE_NAME, mappings=global_mappings))

    if "profiles" in data:
        for profile_data in data["profiles"]:
            mappings = _parse_mappings(profile_data["mappings"])
            profiles.append(
                Profile(app_name=profile_data["app_name"], mappings=mappings),
            )

    return Configuration(profiles=tuple(profiles))


def _parse_mappings(mappings_data: dict[str, Any]) -> dict[str, Action]:
    mappings: dict[str, Action] = {}
    for event_key, action_data in mappings_data.items():
        action_type_str = action_data["type"]
        action_type = (
            ActionType.KEYBOARD if action_type_str == "keyboard" else ActionType.COMMAND
        )
        mappings[event_key] = Action(
            action_type=action_type,
            payload=action_data["payload"],
        )
    return mappings
