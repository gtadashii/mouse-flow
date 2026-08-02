from __future__ import annotations

from mouseflow.domain import (
    Action,
    DispatchContext,
    EventType,
    Gesture,
    MouseEvent,
    Profile,
)


def resolve_action(
    context: DispatchContext,
    profile: Profile | None,
) -> Action | None:
    if profile is None:
        return None

    if isinstance(context.event, Gesture):
        return profile.gesture_mappings.get(context.event.direction)
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
