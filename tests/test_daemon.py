from __future__ import annotations

import logging
import os
import signal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from mouseflow.daemon import (
    Daemon,
    DaemonError,
    DaemonInitializationError,
    DaemonRuntimeError,
    DaemonState,
    setup_logging,
)
from mouseflow.discovery import SupportedDevice
from mouseflow.domain import Configuration


class TestDaemonState:
    def test_state_values(self) -> None:
        assert DaemonState.INITIALIZING.value == "INITIALIZING"
        assert DaemonState.RUNNING.value == "RUNNING"
        assert DaemonState.SHUTTING_DOWN.value == "SHUTTING_DOWN"
        assert DaemonState.STOPPED.value == "STOPPED"


class TestDaemonExceptions:
    def test_daemon_error_is_exception(self) -> None:
        assert issubclass(DaemonError, Exception)

    def test_daemon_initialization_error_is_daemon_error(self) -> None:
        assert issubclass(DaemonInitializationError, DaemonError)

    def test_daemon_runtime_error_is_daemon_error(self) -> None:
        assert issubclass(DaemonRuntimeError, DaemonError)


class TestSetupLogging:
    def test_configures_root_logger(self) -> None:
        with patch("mouseflow.daemon.logging.basicConfig") as mock_config:
            setup_logging()
            mock_config.assert_called_once()

    def test_sets_default_level_to_info(self) -> None:
        with patch("mouseflow.daemon.logging.basicConfig") as mock_config:
            setup_logging()
            call_kwargs = mock_config.call_args
            assert call_kwargs.kwargs["level"] == logging.INFO

    def test_sets_debug_level_when_requested(self) -> None:
        with patch("mouseflow.daemon.logging.basicConfig") as mock_config:
            setup_logging(level=logging.DEBUG)
            call_kwargs = mock_config.call_args
            assert call_kwargs.kwargs["level"] == logging.DEBUG

    def test_sets_format_with_timestamp_and_level(self) -> None:
        with patch("mouseflow.daemon.logging.basicConfig") as mock_config:
            setup_logging()
            call_kwargs = mock_config.call_args
            fmt = call_kwargs.kwargs["format"]
            assert "%(asctime)s" in fmt
            assert "%(levelname)s" in fmt
            assert "%(name)s" in fmt
            assert "%(message)s" in fmt

    def test_reads_log_level_from_environment(self) -> None:
        with (
            patch.dict(os.environ, {"MOUSEFLOW_LOG_LEVEL": "DEBUG"}),
            patch("mouseflow.daemon.logging.basicConfig") as mock_config,
        ):
            setup_logging()
            call_kwargs = mock_config.call_args
            assert call_kwargs.kwargs["level"] == logging.DEBUG

    def test_invalid_env_level_defaults_to_info(self) -> None:
        with (
            patch.dict(os.environ, {"MOUSEFLOW_LOG_LEVEL": "INVALID"}),
            patch("mouseflow.daemon.logging.basicConfig") as mock_config,
        ):
            setup_logging()
            call_kwargs = mock_config.call_args
            assert call_kwargs.kwargs["level"] == logging.INFO


class TestDaemonStartup:
    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_startup_finds_device(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        mock_find.assert_called_once()
        assert daemon._device is not None
        assert daemon._device.name == "Test Mouse"

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_startup_loads_config(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        mock_parse.assert_called_once()
        assert daemon._config is not None

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_startup_creates_resolver(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        assert daemon._resolver is not None

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_startup_creates_dispatcher(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        assert daemon._dispatcher is not None

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_startup_creates_profile_resolver(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        assert daemon._profile_resolver is not None

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_startup_failure_no_device(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = None

        daemon = Daemon()

        with pytest.raises(DaemonInitializationError, match="No supported mouse found"):
            daemon._initialize()

        mock_parse.assert_not_called()

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_startup_sets_initializing_state(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        assert daemon._state == DaemonState.STOPPED

        daemon._initialize()

        assert daemon._state == DaemonState.INITIALIZING  # type: ignore[comparison-overlap]


class TestDaemonShutdown:
    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_shutdown_sets_state_to_stopped(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()
        daemon._state = DaemonState.RUNNING

        daemon._shutdown()

        assert daemon._state == DaemonState.STOPPED

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_shutdown_is_idempotent(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        daemon._shutdown()
        daemon._shutdown()

        assert daemon._state == DaemonState.STOPPED


class TestDaemonSignalHandling:
    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_registers_sigterm_handler(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        with patch("signal.signal") as mock_signal:
            daemon._register_signal_handlers()
            mock_signal.assert_any_call(signal.SIGTERM, daemon._handle_signal)

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_registers_sigint_handler(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        with patch("signal.signal") as mock_signal:
            daemon._register_signal_handlers()
            mock_signal.assert_any_call(signal.SIGINT, daemon._handle_signal)

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_signal_handler_triggers_shutdown(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()
        daemon._state = DaemonState.RUNNING

        daemon._handle_signal(signal.SIGTERM, None)

        assert daemon._state == DaemonState.STOPPED

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_sigint_triggers_shutdown(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()
        daemon._state = DaemonState.RUNNING

        daemon._handle_signal(signal.SIGINT, None)

        assert daemon._state == DaemonState.STOPPED

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_event_loop_stops_on_shutdown_signal(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        from mouseflow.domain import DispatchContext, InputIdentifier, UserInput

        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        events = [
            DispatchContext(event=UserInput(identifier=InputIdentifier.BTN_SIDE)),
            DispatchContext(event=UserInput(identifier=InputIdentifier.BTN_EXTRA)),
        ]

        def stop_after_first_event(_events: Any) -> Any:
            daemon._state = DaemonState.STOPPED
            return iter(events)

        mock_dispatcher = MagicMock()
        mock_dispatcher.dispatch.side_effect = stop_after_first_event
        daemon._dispatcher = mock_dispatcher

        daemon._state = DaemonState.RUNNING
        daemon._run_event_loop()

        assert daemon._state == DaemonState.STOPPED


class TestDaemonResourceCleanup:
    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_device_closed_on_shutdown(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_device_info = SupportedDevice(name="Test Mouse", path="/dev/input/event0")
        mock_find.return_value = mock_device_info
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        with patch("mouseflow.daemon.read_events_with_gestures") as mock_read:
            mock_read.return_value = iter([])
            daemon._state = DaemonState.RUNNING
            daemon._run_event_loop()

        mock_read.assert_called_once_with(mock_device_info.path)

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_daemon_shutdown_logs_message(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()
        daemon._state = DaemonState.RUNNING

        with patch("mouseflow.daemon.logger") as mock_logger:
            daemon._shutdown()
            mock_logger.info.assert_any_call("Shutting down MouseFlow daemon...")

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_run_calls_shutdown_in_finally(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()

        with (
            patch.object(
                daemon, "_run_event_loop", side_effect=Exception("test error")
            ),
            patch.object(daemon, "_shutdown") as mock_shutdown,
        ):
            with pytest.raises(Exception, match="test error"):
                daemon.run()
            mock_shutdown.assert_called_once()


class TestDaemonFailureHandling:
    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_device_disconnection_raises_runtime_error(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()
        daemon._initialize()

        mock_dispatcher = MagicMock()
        mock_dispatcher.dispatch.side_effect = OSError("Device disconnected")
        daemon._dispatcher = mock_dispatcher

        with pytest.raises(DaemonRuntimeError, match="Device disconnected"):
            daemon._run_event_loop()

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_config_error_raises_initialization_error(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        from mouseflow.parser import ConfigurationError

        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.side_effect = ConfigurationError("Invalid config")

        daemon = Daemon()

        with pytest.raises(ConfigurationError):
            daemon._initialize()

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_resolver_failure_handled_gracefully(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        def failing_resolver_factory() -> None:
            raise Exception("Cannot connect to compositor")

        daemon = Daemon(resolver_factory=failing_resolver_factory)

        with pytest.raises(Exception, match="Cannot connect to compositor"):
            daemon._initialize()

    def test_run_event_loop_without_init_raises_error(self) -> None:
        daemon = Daemon()

        with pytest.raises(DaemonRuntimeError, match="Daemon not initialized"):
            daemon._run_event_loop()


class TestDaemonLifecycle:
    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_run_initializes_components(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()

        with patch.object(daemon, "_run_event_loop"):
            daemon.run()

        assert daemon._device is not None
        assert daemon._config is not None

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_run_starts_event_loop(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()

        with patch.object(daemon, "_run_event_loop") as mock_loop:
            daemon.run()
            mock_loop.assert_called_once()

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_run_registers_signal_handlers(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()

        with (
            patch.object(daemon, "_register_signal_handlers") as mock_register,
            patch.object(daemon, "_run_event_loop"),
        ):
            daemon.run()
            mock_register.assert_called_once()

    @patch("mouseflow.daemon.parse_config")
    @patch("mouseflow.daemon.find_supported_device")
    def test_run_sets_running_state(
        self, mock_find: MagicMock, mock_parse: MagicMock
    ) -> None:
        mock_find.return_value = SupportedDevice(
            name="Test Mouse", path="/dev/input/event0"
        )
        mock_parse.return_value = Configuration()

        daemon = Daemon()

        with patch.object(daemon, "_run_event_loop"):
            daemon.run()

        assert daemon._state == DaemonState.STOPPED
