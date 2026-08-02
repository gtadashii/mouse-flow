from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from mouseflow.domain import (
    Action,
    ActionExecutor,
    ActionType,
    ExecutionResult,
    ExecutionStatus,
    keyboard_action,
)
from mouseflow.runner import (
    ActionRunner,
    KeyboardAdapter,
    ShellAdapter,
    format_execution_result,
)


def _mock_keyboard() -> MagicMock:
    return MagicMock()


def _create_keyboard_adapter_with_mock(
    mock_keyboard: MagicMock,
) -> KeyboardAdapter:
    key_map = {
        "ctrl": "MOCK_CTRL",
        "alt": "MOCK_ALT",
        "shift": "MOCK_SHIFT",
        "p": "MOCK_P",
        "left": "MOCK_LEFT",
        "c": "MOCK_C",
    }
    return KeyboardAdapter(controller=mock_keyboard, key_map=key_map)


class TestKeyboardAdapter:
    def test_keyboard_shortcut_executed_successfully(self) -> None:
        action = keyboard_action("a")
        mock_keyboard = _mock_keyboard()
        adapter = KeyboardAdapter(controller=mock_keyboard, key_map={})

        result = adapter.execute(action)

        assert result.status == ExecutionStatus.SUCCESS
        assert result.action == action
        assert mock_keyboard.press.called
        assert mock_keyboard.release.called

    def test_complex_key_combination(self) -> None:
        action = keyboard_action("ctrl+shift+p")
        mock_keyboard = _mock_keyboard()
        adapter = _create_keyboard_adapter_with_mock(mock_keyboard)

        result = adapter.execute(action)

        assert result.status == ExecutionStatus.SUCCESS
        assert mock_keyboard.press.call_count >= 3
        assert mock_keyboard.release.call_count >= 3

    def test_keyboard_execution_failure(self) -> None:
        action = keyboard_action("invalid_key_that_does_not_exist")
        mock_keyboard = _mock_keyboard()
        adapter = KeyboardAdapter(controller=mock_keyboard, key_map={})

        result = adapter.execute(action)

        assert result.status == ExecutionStatus.FAILURE
        assert result.error_message is not None
        assert "Unknown key" in result.error_message

    def test_modifier_keys_recognized(self) -> None:
        action = keyboard_action("alt+left")
        mock_keyboard = _mock_keyboard()
        adapter = _create_keyboard_adapter_with_mock(mock_keyboard)

        result = adapter.execute(action)

        assert result.status == ExecutionStatus.SUCCESS

    def test_single_key_execution(self) -> None:
        action = keyboard_action("a")
        mock_keyboard = _mock_keyboard()
        adapter = KeyboardAdapter(controller=mock_keyboard, key_map={})

        result = adapter.execute(action)

        assert result.status == ExecutionStatus.SUCCESS
        assert mock_keyboard.press.call_count == 1
        assert mock_keyboard.release.call_count == 1


class TestShellAdapter:
    def test_command_executed_successfully(self) -> None:
        from mouseflow.domain import command_action

        action = command_action("echo 'test'")
        adapter = ShellAdapter()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = adapter.execute(action)

            assert result.status == ExecutionStatus.SUCCESS
            assert result.action == action
            mock_run.assert_called_once()

    def test_command_with_arguments(self) -> None:
        from mouseflow.domain import command_action

        action = command_action("swaymsg workspace next")
        adapter = ShellAdapter()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = adapter.execute(action)

            assert result.status == ExecutionStatus.SUCCESS
            call_args = mock_run.call_args
            assert call_args[0][0] == "swaymsg workspace next"

    def test_command_execution_failure(self) -> None:
        from mouseflow.domain import command_action

        action = command_action("nonexistent_command_12345")
        adapter = ShellAdapter()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=127,
                stderr="command not found",
            )
            result = adapter.execute(action)

            assert result.status == ExecutionStatus.FAILURE
            assert result.error_message is not None

    def test_command_timeout(self) -> None:
        from mouseflow.domain import command_action

        action = command_action("sleep 100")
        adapter = ShellAdapter(timeout=10)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd="sleep 100",
                timeout=10,
            )
            result = adapter.execute(action)

            assert result.status == ExecutionStatus.FAILURE
            assert result.error_message is not None
            assert "timed out" in result.error_message.lower()


class TestActionRunner:
    def test_keyboard_action_dispatched(self) -> None:
        action = keyboard_action("a")
        mock_keyboard = _mock_keyboard()
        keyboard_adapter = KeyboardAdapter(controller=mock_keyboard, key_map={})

        executors = {ActionType.KEYBOARD: keyboard_adapter}
        runner = ActionRunner(executors=executors)

        result = runner.run(action)
        assert result.status == ExecutionStatus.SUCCESS

    def test_command_action_dispatched(self) -> None:
        from mouseflow.domain import command_action

        action = command_action("echo test")
        shell_adapter = ShellAdapter()

        executors = {ActionType.COMMAND: shell_adapter}
        runner = ActionRunner(executors=executors)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = runner.run(action)

            assert result.status == ExecutionStatus.SUCCESS

    def test_unknown_action_type(self) -> None:
        action = Action(action_type="UNKNOWN", payload="test")  # type: ignore[arg-type]
        runner = ActionRunner(executors={})

        result = runner.run(action)

        assert result.status == ExecutionStatus.FAILURE
        assert result.error_message is not None
        assert "Unknown action type" in result.error_message


class TestExecutionResultReporting:
    def test_successful_execution_reported(self) -> None:
        action = keyboard_action("ctrl+c")
        result = ExecutionResult(action=action, status=ExecutionStatus.SUCCESS)

        report = format_execution_result(result)

        assert "ctrl+c" in report
        assert "Executed" in report

    def test_failed_execution_reported(self) -> None:
        action = keyboard_action("invalid")
        result = ExecutionResult(
            action=action,
            status=ExecutionStatus.FAILURE,
            error_message="Unknown key: invalid",
        )

        report = format_execution_result(result)

        assert "invalid" in report
        assert "Failed" in report
        assert "Unknown key: invalid" in report


class TestGracefulFailureHandling:
    def test_execution_failure_does_not_terminate(self) -> None:
        action = keyboard_action("invalid_key")
        mock_keyboard = _mock_keyboard()
        adapter = KeyboardAdapter(controller=mock_keyboard, key_map={})

        result = adapter.execute(action)

        assert result.status == ExecutionStatus.FAILURE
        assert result.error_message is not None

    def test_repeated_failures_handled_gracefully(self) -> None:
        actions = [
            keyboard_action("invalid1"),
            keyboard_action("invalid2"),
            keyboard_action("invalid3"),
        ]
        mock_keyboard = _mock_keyboard()
        adapter = KeyboardAdapter(controller=mock_keyboard, key_map={})

        results = []
        for action in actions:
            result = adapter.execute(action)
            results.append(result)

        assert len(results) == 3
        for result in results:
            assert result.status == ExecutionStatus.FAILURE
            assert result.error_message is not None


class TestPipelineIntegration:
    def test_full_pipeline_with_keyboard_action(self) -> None:
        from mouseflow.domain import (
            Application,
            Configuration,
            DispatchContext,
            MouseButton,
            MouseEvent,
            Profile,
            Window,
            WindowInfo,
        )
        from mouseflow.loader import resolve_action

        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                    },
                ),
            ),
        )

        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)
        assert action is not None

        mock_keyboard = _mock_keyboard()
        adapter = _create_keyboard_adapter_with_mock(mock_keyboard)
        executors = {ActionType.KEYBOARD: adapter}
        runner = ActionRunner(executors=executors)

        result = runner.run(action)

        assert result.status == ExecutionStatus.SUCCESS
        assert result.action.payload == "alt+left"

    def test_full_pipeline_with_shell_command(self) -> None:
        from mouseflow.domain import (
            Application,
            Configuration,
            DispatchContext,
            MouseButton,
            MouseEvent,
            Profile,
            Window,
            WindowInfo,
            command_action,
        )
        from mouseflow.loader import resolve_action

        config = Configuration(
            profiles=(
                Profile(
                    app_name="terminal",
                    mappings={
                        "BTN_EXTRA": command_action("echo 'test'"),
                    },
                ),
            ),
        )

        event = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        window_info = WindowInfo(
            application=Application(app_name="terminal"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)
        assert action is not None

        shell_adapter = ShellAdapter()
        executors = {ActionType.COMMAND: shell_adapter}
        runner = ActionRunner(executors=executors)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = runner.run(action)

            assert result.status == ExecutionStatus.SUCCESS
            assert result.action.payload == "echo 'test'"

    def test_full_pipeline_with_application_launch(self) -> None:
        from mouseflow.domain import (
            Application,
            Configuration,
            DispatchContext,
            MouseButton,
            MouseEvent,
            Profile,
            Window,
            WindowInfo,
            command_action,
        )
        from mouseflow.loader import resolve_action

        config = Configuration(
            profiles=(
                Profile(
                    app_name="desktop",
                    mappings={
                        "BTN_FORWARD": command_action("firefox"),
                    },
                ),
            ),
        )

        event = MouseEvent.button_event(MouseButton.BTN_FORWARD)
        window_info = WindowInfo(
            application=Application(app_name="desktop"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)
        assert action is not None

        shell_adapter = ShellAdapter()
        executors = {ActionType.COMMAND: shell_adapter}
        runner = ActionRunner(executors=executors)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = runner.run(action)

            assert result.status == ExecutionStatus.SUCCESS
            assert result.action.payload == "firefox"

    def test_pipeline_with_mixed_action_types(self) -> None:
        from mouseflow.domain import (
            Application,
            Configuration,
            DispatchContext,
            MouseButton,
            MouseEvent,
            Profile,
            Window,
            WindowInfo,
            command_action,
        )
        from mouseflow.loader import resolve_action

        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                        "BTN_EXTRA": command_action("echo 'test'"),
                    },
                ),
            ),
        )

        mock_keyboard = _mock_keyboard()
        keyboard_adapter = _create_keyboard_adapter_with_mock(mock_keyboard)
        shell_adapter = ShellAdapter()
        executors: dict[ActionType, ActionExecutor] = {
            ActionType.KEYBOARD: keyboard_adapter,
            ActionType.COMMAND: shell_adapter,
        }
        runner = ActionRunner(executors=executors)

        event1 = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context1 = DispatchContext(event=event1, window_info=window_info)

        action1 = resolve_action(context1, config)
        assert action1 is not None

        result1 = runner.run(action1)
        assert result1.status == ExecutionStatus.SUCCESS

        event2 = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        context2 = DispatchContext(event=event2, window_info=window_info)

        action2 = resolve_action(context2, config)
        assert action2 is not None

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result2 = runner.run(action2)
            assert result2.status == ExecutionStatus.SUCCESS

    def test_pipeline_resilience_with_simulated_failures(self) -> None:
        from mouseflow.domain import (
            Application,
            Configuration,
            DispatchContext,
            MouseButton,
            MouseEvent,
            Profile,
            Window,
            WindowInfo,
            command_action,
        )
        from mouseflow.loader import resolve_action

        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": command_action("nonexistent_command"),
                    },
                ),
            ),
        )

        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        action = resolve_action(context, config)
        assert action is not None

        shell_adapter = ShellAdapter()
        executors = {ActionType.COMMAND: shell_adapter}
        runner = ActionRunner(executors=executors)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=127,
                stderr="command not found",
            )

            result = runner.run(action)

            assert result.status == ExecutionStatus.FAILURE
            assert result.error_message is not None

        action2 = resolve_action(context, config)
        assert action2 is not None

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result2 = runner.run(action2)
            assert result2.status == ExecutionStatus.SUCCESS
