from __future__ import annotations

from collections.abc import Generator, Iterable

from mouseflow.domain import (
    GLOBAL_PROFILE_NAME,
    DispatchContext,
    Profile,
    UserInput,
)
from mouseflow.resolver import WindowResolver


class EventDispatcher:
    def __init__(self, resolver: WindowResolver) -> None:
        self._resolver = resolver

    def dispatch(
        self,
        events: Iterable[UserInput],
    ) -> Generator[DispatchContext]:
        for event in events:
            window_info = self._resolver.resolve()
            yield DispatchContext(event=event, window_info=window_info)


def format_dispatch_context(
    context: DispatchContext,
    profile: Profile | None = None,
) -> str:
    identifier_str = context.event.identifier.value

    if context.window_info is None:
        return f"Application: Unknown\nTitle: Unknown\nInput: {identifier_str}"

    app_name = context.window_info.application.app_name
    title = context.window_info.window.title

    lines = [
        f"Application: {app_name}",
        f"Title: {title}",
        f"Input: {identifier_str}",
    ]

    if profile is not None:
        if profile.app_name == GLOBAL_PROFILE_NAME:
            lines.append("Profile: global")
        else:
            lines.append(f"Profile: {profile.app_name}")

    return "\n".join(lines)
