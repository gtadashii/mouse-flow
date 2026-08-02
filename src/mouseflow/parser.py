from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mouseflow.domain import Action, ActionType, Configuration, Profile


class ConfigurationError(Exception):
    pass


class ValidationError(ConfigurationError):
    pass


def parse_config(path: Path) -> Configuration:
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


def _validate_structure(data: dict[str, Any]) -> None:
    if "profiles" not in data:
        raise ValidationError("Missing required field: profiles")

    profiles = data["profiles"]
    if not isinstance(profiles, list):
        raise ValidationError("profiles must be a list")

    for i, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            raise ValidationError(f"Profile {i} must be a mapping")

        if "app_name" not in profile:
            raise ValidationError(f"Profile {i} missing required field: app_name")

        if "mappings" not in profile:
            raise ValidationError(f"Profile {i} missing required field: mappings")

        mappings = profile["mappings"]
        if not isinstance(mappings, dict):
            raise ValidationError(f"Profile {i} mappings must be a mapping")

        for event_key, action in mappings.items():
            if not isinstance(action, dict):
                msg = f"Mapping {event_key} in profile {i} must be a mapping"
                raise ValidationError(msg)

            if "type" not in action:
                msg = f"Mapping {event_key} in profile {i} missing required field: type"
                raise ValidationError(msg)

            if "payload" not in action:
                msg = (
                    f"Mapping {event_key} in profile {i} "
                    "missing required field: payload"
                )
                raise ValidationError(msg)

            action_type = action["type"]
            if action_type not in ("keyboard", "command"):
                msg = (
                    f"Mapping {event_key} in profile {i} "
                    f"has invalid action type: {action_type}"
                )
                raise ValidationError(msg)


def _translate_to_domain(data: dict[str, Any]) -> Configuration:
    profiles: list[Profile] = []

    for profile_data in data["profiles"]:
        mappings: dict[str, Action] = {}

        for event_key, action_data in profile_data["mappings"].items():
            action_type_str = action_data["type"]
            action_type = (
                ActionType.KEYBOARD
                if action_type_str == "keyboard"
                else ActionType.COMMAND
            )
            mappings[event_key] = Action(
                action_type=action_type,
                payload=action_data["payload"],
            )

        profiles.append(
            Profile(app_name=profile_data["app_name"], mappings=mappings),
        )

    return Configuration(profiles=tuple(profiles))
