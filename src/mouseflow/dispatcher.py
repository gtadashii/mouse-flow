from __future__ import annotations

from collections.abc import Generator, Iterable

from mouseflow.domain import (
    DispatchContext,
    EventType,
    Gesture,
    MouseEvent,
    Profile,
)
from mouseflow.resolver import WindowResolver


class EventDispatcher:
    def __init__(self, resolver: WindowResolver) -> None:
        self._resolver = resolver

    def dispatch(
        self,
        events: Iterable[MouseEvent | Gesture],
    ) -> Generator[DispatchContext]:
        for event in events:
            window_info = self._resolver.resolve()
            yield DispatchContext(event=event, window_info=window_info)


def format_dispatch_context(
    context: DispatchContext,
    profile: Profile | None = None,
) -> str:
    if isinstance(context.event, Gesture):
        return _format_gesture_context(context, profile)
    return _format_mouse_context(context, profile)


def _format_mouse_context(
    context: DispatchContext,
    profile: Profile | None = None,
) -> str:
    event = context.event
    if isinstance(event, Gesture):
        return _format_gesture_context(context, profile)

    event_str = "Unknown"

    if event.event_type == EventType.BUTTON:
        event_str = event.button.value if event.button else "Unknown"
    elif event.event_type == EventType.WHEEL:
        event_str = event.wheel.value if event.wheel else "Unknown"

    if context.window_info is None:
        return f"Application: Unknown\nTitle: Unknown\nEvent: {event_str}"

    app_name = context.window_info.application.app_name
    title = context.window_info.window.title

    lines = [f"Application: {app_name}", f"Title: {title}", f"Event: {event_str}"]

    if profile is not None:
        from mouseflow.domain import GLOBAL_PROFILE_NAME

        if profile.app_name == GLOBAL_PROFILE_NAME:
            lines.append("Profile: global")
        else:
            lines.append(f"Profile: {profile.app_name}")

    return "\n".join(lines)


def _format_gesture_context(
    context: DispatchContext,
    profile: Profile | None = None,
) -> str:
    event = context.event
    if isinstance(event, MouseEvent):
        return _format_mouse_context(context, profile)

    direction_str = event.direction.value

    if context.window_info is None:
        return f"Application: Unknown\nTitle: Unknown\nGesture: {direction_str}"

    app_name = context.window_info.application.app_name
    title = context.window_info.window.title

    lines = [
        f"Application: {app_name}",
        f"Title: {title}",
        f"Gesture: {direction_str}",
    ]

    if profile is not None:
        from mouseflow.domain import GLOBAL_PROFILE_NAME

        if profile.app_name == GLOBAL_PROFILE_NAME:
            lines.append("Profile: global")
        else:
            lines.append(f"Profile: {profile.app_name}")

    return "\n".join(lines)
