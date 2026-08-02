from __future__ import annotations

from mouseflow.domain import (
    Action,
    Configuration,
    DispatchContext,
    EventType,
    MouseEvent,
)


def resolve_action(
    context: DispatchContext,
    config: Configuration,
) -> Action | None:
    if context.window_info is None:
        return None

    profile = config.get_profile(context.window_info.application.app_name)
    if profile is None:
        return None

    event_key = _extract_event_key(context.event)
    if event_key is None:
        return None

    return profile.mappings.get(event_key)


def _extract_event_key(event: MouseEvent) -> str | None:
    if event.event_type == EventType.BUTTON:
        if event.button is None:
            return None
        return event.button.value

    if event.event_type == EventType.WHEEL:
        if event.wheel is None:
            return None
        return event.wheel.value

    return None
