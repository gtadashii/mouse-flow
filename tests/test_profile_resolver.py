from __future__ import annotations

from mouseflow.domain import (
    GLOBAL_PROFILE_NAME,
    Application,
    Configuration,
    Profile,
    Window,
    WindowInfo,
    keyboard_action,
)
from mouseflow.profile_resolver import DefaultProfileResolver, format_profile_name


class TestProfileResolver:
    def test_resolve_application_specific_profile_exists(self) -> None:
        firefox_profile = Profile(
            app_name="firefox",
            mappings={"BTN_SIDE": keyboard_action("alt+left")},
        )
        config = Configuration(profiles=(firefox_profile,))
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = DefaultProfileResolver()

        result = resolver.resolve(config, window_info)

        assert result == firefox_profile

    def test_resolve_application_profile_selected_over_global(self) -> None:
        firefox_profile = Profile(
            app_name="firefox",
            mappings={"BTN_SIDE": keyboard_action("alt+left")},
        )
        global_profile = Profile(
            app_name=GLOBAL_PROFILE_NAME,
            mappings={"BTN_SIDE": keyboard_action("ctrl+left")},
        )
        config = Configuration(profiles=(firefox_profile, global_profile))
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = DefaultProfileResolver()

        result = resolver.resolve(config, window_info)

        assert result == firefox_profile
        assert result != global_profile

    def test_resolve_global_profile_fallback(self) -> None:
        global_profile = Profile(
            app_name=GLOBAL_PROFILE_NAME,
            mappings={"BTN_SIDE": keyboard_action("ctrl+left")},
        )
        config = Configuration(profiles=(global_profile,))
        window_info = WindowInfo(
            application=Application(app_name="chrome"),
            window=Window(title="Test"),
        )
        resolver = DefaultProfileResolver()

        result = resolver.resolve(config, window_info)

        assert result == global_profile

    def test_resolve_global_profile_for_unknown_application(self) -> None:
        global_profile = Profile(
            app_name=GLOBAL_PROFILE_NAME,
            mappings={"BTN_SIDE": keyboard_action("ctrl+left")},
        )
        config = Configuration(profiles=(global_profile,))
        window_info = WindowInfo(
            application=Application(app_name="Unknown"),
            window=Window(title="Test"),
        )
        resolver = DefaultProfileResolver()

        result = resolver.resolve(config, window_info)

        assert result == global_profile

    def test_resolve_no_profiles_configured(self) -> None:
        config = Configuration()
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = DefaultProfileResolver()

        result = resolver.resolve(config, window_info)

        assert result is None

    def test_resolve_no_matching_profile_no_global(self) -> None:
        firefox_profile = Profile(
            app_name="firefox",
            mappings={"BTN_SIDE": keyboard_action("alt+left")},
        )
        config = Configuration(profiles=(firefox_profile,))
        window_info = WindowInfo(
            application=Application(app_name="chrome"),
            window=Window(title="Test"),
        )
        resolver = DefaultProfileResolver()

        result = resolver.resolve(config, window_info)

        assert result is None

    def test_resolve_null_window_info(self) -> None:
        firefox_profile = Profile(
            app_name="firefox",
            mappings={"BTN_SIDE": keyboard_action("alt+left")},
        )
        global_profile = Profile(
            app_name=GLOBAL_PROFILE_NAME,
            mappings={"BTN_SIDE": keyboard_action("ctrl+left")},
        )
        config = Configuration(profiles=(firefox_profile, global_profile))
        resolver = DefaultProfileResolver()

        result = resolver.resolve(config, None)

        assert result is None

    def test_resolve_deterministic_precedence(self) -> None:
        firefox_profile = Profile(
            app_name="firefox",
            mappings={"BTN_SIDE": keyboard_action("alt+left")},
        )
        global_profile = Profile(
            app_name=GLOBAL_PROFILE_NAME,
            mappings={"BTN_SIDE": keyboard_action("ctrl+left")},
        )
        config = Configuration(profiles=(firefox_profile, global_profile))
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        resolver = DefaultProfileResolver()

        result1 = resolver.resolve(config, window_info)
        result2 = resolver.resolve(config, window_info)
        result3 = resolver.resolve(config, window_info)

        assert result1 == result2 == result3 == firefox_profile


class TestFormatProfileName:
    def test_format_application_profile(self) -> None:
        profile = Profile(app_name="firefox", mappings={})
        assert format_profile_name(profile) == "firefox"

    def test_format_global_profile(self) -> None:
        profile = Profile(app_name=GLOBAL_PROFILE_NAME, mappings={})
        assert format_profile_name(profile) == "global"

    def test_format_none_profile(self) -> None:
        assert format_profile_name(None) == "none"
