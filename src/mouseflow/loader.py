from __future__ import annotations

from mouseflow.domain import (
    Action,
    DispatchContext,
    Profile,
)


def resolve_action(
    context: DispatchContext,
    profile: Profile | None,
) -> Action | None:
    if profile is None:
        return None
    return profile.mappings.get(context.event.identifier)
