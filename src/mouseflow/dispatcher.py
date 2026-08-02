from __future__ import annotations

from collections.abc import Generator, Iterable

from mouseflow.domain import DispatchContext, EventType, MouseEvent
from mouseflow.resolver import WindowResolver


class EventDispatcher:
    def __init__(self, resolver: WindowResolver) -> None:
        self._resolver = resolver

    def dispatch(self, events: Iterable[MouseEvent]) -> Generator[DispatchContext]:
        for event in events:
            window_info = self._resolver.resolve()
            yield DispatchContext(event=event, window_info=window_info)


def format_dispatch_context(context: DispatchContext) -> str:
    event = context.event
    event_str = "Unknown"

    if event.event_type == EventType.BUTTON:
        event_str = event.button.value if event.button else "Unknown"
    elif event.event_type == EventType.WHEEL:
        event_str = event.wheel.value if event.wheel else "Unknown"

    if context.window_info is None:
        return f"Application: Unknown\nTitle: Unknown\nEvent: {event_str}"

    app_name = context.window_info.application.app_name
    title = context.window_info.window.title

    return f"Application: {app_name}\nTitle: {title}\nEvent: {event_str}"
