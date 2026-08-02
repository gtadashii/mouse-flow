from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mouseflow.domain import (
    Action,
    ActionType,
    Configuration,
    InputIdentifier,
    Profile,
)

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "mouseflow" / "config.yaml"

GESTURE_PREFIXES = {
    "UP": "GESTURE_UP",
    "DOWN": "GESTURE_DOWN",
    "LEFT": "GESTURE_LEFT",
    "RIGHT": "GESTURE_RIGHT",
}


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
    try:
        with path.open() as f:
            data = yaml.safe_load(f)
            if data is None:
                return {}
            return data  # type: ignore[no-any-return]
    except FileNotFoundError as e:
        raise ConfigurationError(f"Configuration file not found: {path}") from e
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in configuration file: {e}") from e


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
            if app_name == "global":
                raise ValidationError(
                    f"Profile {i} cannot use reserved name 'global'. "
                    "Use 'global:' key at top level instead.",
                )

            if "mappings" not in profile:
                raise ValidationError(f"Profile {i} missing required field: mappings")

            mappings = profile["mappings"]
            if not isinstance(mappings, dict):
                raise ValidationError(f"Profile {i} mappings must be a mapping")

            for event_key, action in mappings.items():
                _validate_action_mapping(event_key, action, f"profile {i}")

            if "gestures" in profile:
                gestures = profile["gestures"]
                if not isinstance(gestures, dict):
                    raise ValidationError(f"Profile {i} gestures must be a mapping")

                for direction, action in gestures.items():
                    _validate_gesture_mapping(direction, action, f"profile {i}")

    if "global" in data:
        global_mappings = data["global"]
        if not isinstance(global_mappings, dict):
            raise ValidationError("global must be a mapping")

        for event_key, action in global_mappings.items():
            _validate_action_mapping(event_key, action, "global")

        if "global_gestures" in data:
            global_gestures = data["global_gestures"]
            if not isinstance(global_gestures, dict):
                raise ValidationError("global_gestures must be a mapping")

            for direction, action in global_gestures.items():
                _validate_gesture_mapping(direction, action, "global")


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


def _validate_gesture_mapping(
    direction: str,
    action: Any,
    context: str,
) -> None:
    valid_directions = {"UP", "DOWN", "LEFT", "RIGHT"}
    if direction not in valid_directions:
        raise ValidationError(
            f"Gesture {direction} in {context} is invalid. "
            f"Must be one of: {', '.join(sorted(valid_directions))}",
        )

    _validate_action_mapping(direction, action, context)


def _to_input_identifier(key: str, is_gesture: bool = False) -> InputIdentifier:
    if is_gesture:
        gesture_key = GESTURE_PREFIXES.get(key)
        if gesture_key is not None:
            return InputIdentifier[gesture_key]
    return InputIdentifier[key]


def _translate_to_domain(data: dict[str, Any]) -> Configuration:
    profiles: list[Profile] = []

    if "profiles" in data:
        for profile_data in data["profiles"]:
            mappings = _parse_mappings(profile_data.get("mappings", {}))
            gesture_mappings = _parse_gesture_mappings(profile_data.get("gestures", {}))
            all_mappings = {**mappings, **gesture_mappings}
            profiles.append(
                Profile(
                    app_name=profile_data["app_name"],
                    mappings=all_mappings,
                ),
            )

    if "global" in data:
        mappings = _parse_mappings(data["global"])
        gesture_mappings = _parse_gesture_mappings(data.get("global_gestures", {}))
        all_mappings = {**mappings, **gesture_mappings}
        profiles.append(
            Profile(
                app_name="global",
                mappings=all_mappings,
            ),
        )

    return Configuration(profiles=tuple(profiles))


def _parse_mappings(mappings_data: dict[str, Any]) -> dict[InputIdentifier, Action]:
    mappings: dict[InputIdentifier, Action] = {}
    for event_key, action_data in mappings_data.items():
        identifier = _to_input_identifier(event_key)
        action_type_str = action_data["type"]
        action_type = (
            ActionType.KEYBOARD if action_type_str == "keyboard" else ActionType.COMMAND
        )
        mappings[identifier] = Action(
            action_type=action_type,
            payload=action_data["payload"],
        )
    return mappings


def _parse_gesture_mappings(
    gestures_data: dict[str, Any],
) -> dict[InputIdentifier, Action]:
    gesture_mappings: dict[InputIdentifier, Action] = {}
    for direction_str, action_data in gestures_data.items():
        identifier = _to_input_identifier(direction_str, is_gesture=True)
        action_type_str = action_data["type"]
        action_type = (
            ActionType.KEYBOARD if action_type_str == "keyboard" else ActionType.COMMAND
        )
        gesture_mappings[identifier] = Action(
            action_type=action_type,
            payload=action_data["payload"],
        )
    return gesture_mappings
