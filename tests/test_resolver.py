from unittest.mock import MagicMock, patch

import pytest

from mouseflow.domain import Application, Window, WindowInfo
from mouseflow.resolver import (
    SwayResolver,
    format_window_info,
    resolve_active_window,
)


def test_window_info_creation() -> None:
    app = Application(app_name="Firefox")
    window = Window(title="ChatGPT")
    info = WindowInfo(application=app, window=window)
    assert info.application.app_name == "Firefox"
    assert info.window.title == "ChatGPT"


def test_window_info_immutable() -> None:
    app = Application(app_name="Firefox")
    window = Window(title="ChatGPT")
    info = WindowInfo(application=app, window=window)
    with pytest.raises(AttributeError):
        info.application = Application(app_name="Code")  # type: ignore[misc]


def test_format_window_info() -> None:
    app = Application(app_name="Firefox")
    window = Window(title="ChatGPT")
    info = WindowInfo(application=app, window=window)
    result = format_window_info(info)
    assert result == "Application\nFirefox\n\nTitle\nChatGPT"


def test_format_window_info_with_special_chars() -> None:
    app = Application(app_name="Code")
    window = Window(title="README.md - mouse-flow")
    info = WindowInfo(application=app, window=window)
    result = format_window_info(info)
    assert result == "Application\nCode\n\nTitle\nREADME.md - mouse-flow"


def test_sway_resolver_with_focused_window() -> None:
    mock_focused = MagicMock()
    mock_focused.app_id = "firefox"
    mock_focused.window_class = None
    mock_focused.name = "ChatGPT"

    mock_tree = MagicMock()
    mock_tree.find_focused.return_value = mock_focused

    mock_conn = MagicMock()
    mock_conn.get_tree.return_value = mock_tree

    with patch("mouseflow.resolver.Connection", return_value=mock_conn):
        resolver = SwayResolver()
        result = resolver.resolve()

        assert result is not None
        assert result.application.app_name == "firefox"
        assert result.window.title == "ChatGPT"


def test_sway_resolver_with_window_class_fallback() -> None:
    mock_focused = MagicMock()
    mock_focused.app_id = None
    mock_focused.window_class = "firefox"
    mock_focused.name = "ChatGPT"

    mock_tree = MagicMock()
    mock_tree.find_focused.return_value = mock_focused

    mock_conn = MagicMock()
    mock_conn.get_tree.return_value = mock_tree

    with patch("mouseflow.resolver.Connection", return_value=mock_conn):
        resolver = SwayResolver()
        result = resolver.resolve()

        assert result is not None
        assert result.application.app_name == "firefox"


def test_sway_resolver_with_no_focused_window() -> None:
    mock_tree = MagicMock()
    mock_tree.find_focused.return_value = None

    mock_conn = MagicMock()
    mock_conn.get_tree.return_value = mock_tree

    with patch("mouseflow.resolver.Connection", return_value=mock_conn):
        resolver = SwayResolver()
        result = resolver.resolve()

        assert result is None


def test_sway_resolver_with_missing_app_name() -> None:
    mock_focused = MagicMock()
    mock_focused.app_id = None
    mock_focused.window_class = None
    mock_focused.name = "Untitled Window"

    mock_tree = MagicMock()
    mock_tree.find_focused.return_value = mock_focused

    mock_conn = MagicMock()
    mock_conn.get_tree.return_value = mock_tree

    with patch("mouseflow.resolver.Connection", return_value=mock_conn):
        resolver = SwayResolver()
        result = resolver.resolve()

        assert result is not None
        assert result.application.app_name == "Unknown"


def test_sway_resolver_with_missing_title() -> None:
    mock_focused = MagicMock()
    mock_focused.app_id = "firefox"
    mock_focused.window_class = None
    mock_focused.name = None

    mock_tree = MagicMock()
    mock_tree.find_focused.return_value = mock_focused

    mock_conn = MagicMock()
    mock_conn.get_tree.return_value = mock_tree

    with patch("mouseflow.resolver.Connection", return_value=mock_conn):
        resolver = SwayResolver()
        result = resolver.resolve()

        assert result is not None
        assert result.window.title == "Untitled"


def test_resolve_active_window() -> None:
    app = Application(app_name="firefox")
    window = Window(title="ChatGPT")
    mock_info = WindowInfo(application=app, window=window)

    with patch("mouseflow.resolver.SwayResolver") as mock_resolver_class:
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = mock_info
        mock_resolver_class.return_value = mock_resolver

        result = resolve_active_window()

        assert result == mock_info


def test_resolve_active_window_returns_none() -> None:
    with patch("mouseflow.resolver.SwayResolver") as mock_resolver_class:
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = None
        mock_resolver_class.return_value = mock_resolver

        result = resolve_active_window()

        assert result is None
