from __future__ import annotations

from mouseflow.domain import (
    GLOBAL_PROFILE_NAME,
    Configuration,
    Profile,
    WindowInfo,
)


class ProfileResolver:
    def resolve(
        self,
        configuration: Configuration,
        window_info: WindowInfo | None,
    ) -> Profile | None:
        if window_info is None:
            return None

        app_name = window_info.application.app_name
        app_profile = configuration.get_profile(app_name)

        if app_profile is not None:
            return app_profile

        return configuration.get_global_profile()


def format_profile_name(profile: Profile | None) -> str:
    if profile is None:
        return "none"
    if profile.app_name == GLOBAL_PROFILE_NAME:
        return "global"
    return profile.app_name
