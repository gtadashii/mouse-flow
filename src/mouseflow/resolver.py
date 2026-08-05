from __future__ import annotations

import logging
from typing import Protocol

from i3ipc import Connection

from mouseflow.domain import Application, Window, WindowInfo

logger = logging.getLogger(__name__)


class WindowResolver(Protocol):
    def resolve(self) -> WindowInfo | None: ...


class SwayResolver:
    def __init__(self) -> None:
        try:
            self._conn = Connection()
        except Exception as e:
            logger.warning("Cannot connect to Sway IPC: %s", e)
            self._conn = None

    def resolve(self) -> WindowInfo | None:
        if self._conn is None:
            return None

        try:
            tree = self._conn.get_tree()
            focused = tree.find_focused()

            if focused is None:
                return None

            app_name = focused.app_id or focused.window_class or "Unknown"
            title = focused.name or "Untitled"

            application = Application(app_name=app_name)
            window = Window(title=title)

            return WindowInfo(application=application, window=window)
        except Exception:
            return None


def format_window_info(info: WindowInfo) -> str:
    return f"Application\n{info.application.app_name}\n\nTitle\n{info.window.title}"


def resolve_active_window() -> WindowInfo | None:
    resolver = SwayResolver()
    return resolver.resolve()
