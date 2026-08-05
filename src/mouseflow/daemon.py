from __future__ import annotations

import logging
import os
import signal
from enum import Enum
from typing import Any

from mouseflow.discovery import SupportedDevice, find_supported_device
from mouseflow.dispatcher import EventDispatcher
from mouseflow.domain import Configuration
from mouseflow.engine import read_events_with_gestures
from mouseflow.loader import resolve_action
from mouseflow.parser import parse_config
from mouseflow.profile_resolver import DefaultProfileResolver, ProfileResolver
from mouseflow.resolver import SwayResolver, WindowResolver
from mouseflow.runner import run_action

logger = logging.getLogger(__name__)


class DaemonState(Enum):
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    STOPPED = "STOPPED"


class DaemonError(Exception):
    pass


class DaemonInitializationError(DaemonError):
    pass


class DaemonRuntimeError(DaemonError):
    pass


def setup_logging(level: int | None = None) -> None:
    if level is None:
        env_level = os.environ.get("MOUSEFLOW_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class Daemon:
    def __init__(
        self,
        device_finder: Any = None,
        config_loader: Any = None,
        resolver_factory: Any = None,
        profile_resolver_factory: Any = None,
    ) -> None:
        self._device_finder = device_finder or find_supported_device
        self._config_loader = config_loader or parse_config
        self._resolver_factory = resolver_factory or SwayResolver
        self._profile_resolver_factory = (
            profile_resolver_factory or DefaultProfileResolver
        )

        self._device: SupportedDevice | None = None
        self._config: Configuration | None = None
        self._resolver: WindowResolver | None = None
        self._dispatcher: EventDispatcher | None = None
        self._profile_resolver: ProfileResolver | None = None
        self._state: DaemonState = DaemonState.STOPPED

    def _initialize(self) -> None:
        self._state = DaemonState.INITIALIZING
        logger.info("Initializing MouseFlow daemon...")

        self._device = self._device_finder()
        if self._device is None:
            raise DaemonInitializationError("No supported mouse found.")
        logger.info("Found device: %s", self._device.name)

        self._config = self._config_loader()
        logger.info("Configuration loaded.")

        self._resolver = self._resolver_factory()
        logger.info("Window resolver initialized.")

        self._dispatcher = EventDispatcher(self._resolver)
        logger.info("Event dispatcher initialized.")

        self._profile_resolver = self._profile_resolver_factory()
        logger.info("Profile resolver initialized.")

        logger.info("Initialization complete.")

    def _shutdown(self) -> None:
        if self._state == DaemonState.STOPPED:
            return
        self._state = DaemonState.SHUTTING_DOWN
        logger.info("Shutting down MouseFlow daemon...")
        logger.info("Shutdown complete.")
        self._state = DaemonState.STOPPED

    def _handle_signal(self, signum: int, _frame: Any) -> None:
        sig_name = signal.Signals(signum).name
        logger.info("Received signal %s, initiating shutdown...", sig_name)
        self._shutdown()

    def _register_signal_handlers(self) -> None:
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        logger.info("Signal handlers registered.")

    def _run_event_loop(self) -> None:
        if (
            self._device is None
            or self._config is None
            or self._dispatcher is None
            or self._profile_resolver is None
        ):
            raise DaemonRuntimeError("Daemon not initialized.")

        self._state = DaemonState.RUNNING
        logger.info("Starting event loop...")

        try:
            for context in self._dispatcher.dispatch(
                read_events_with_gestures(self._device.path)
            ):
                if self._state != DaemonState.RUNNING:
                    break

                profile = self._profile_resolver.resolve(
                    self._config, context.window_info
                )
                action = resolve_action(context, profile)
                if action is not None:
                    result = run_action(action)
                    logger.debug("Action executed: %s", result)
        except OSError as e:
            raise DaemonRuntimeError("Device disconnected or unavailable.") from e

        logger.info("Event loop terminated.")

    def run(self) -> None:
        setup_logging()
        try:
            self._initialize()
            self._register_signal_handlers()
            self._run_event_loop()
        finally:
            self._shutdown()
