from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from mouseflow.domain import Action, keyboard_action
from mouseflow.runner import (
    ExecutionResult,
    ExecutionStatus,
    format_execution_result,
    run_action,
)


class TestKeyboardExecution:
    def test_keyboard_shortcut_executed_successfully(self) -> None:
        """Test that a keyboard shortcut is executed successfully."""
        action = keyboard_action("a")

        mock_keyboard = MagicMock()
        with patch(
            "mouseflow.runner._create_keyboard_controller",
            return_value=mock_keyboard,
        ):
            result = run_action(action)

        assert result.status == ExecutionStatus.SUCCESS
        assert result.action == action
        assert mock_keyboard.press.called
        assert mock_keyboard.release.called

    def test_complex_key_combination(self) -> None:
        """Test that a complex key combination with modifiers is executed."""
        action = keyboard_action("ctrl+shift+p")

        mock_keyboard = MagicMock()
        with (
            patch(
                "mouseflow.runner._create_keyboard_controller",
                return_value=mock_keyboard,
            ),
            patch("mouseflow.runner._get_key") as mock_get_key,
        ):
            mock_get_key.side_effect = lambda k: f"key_{k}"
            result = run_action(action)

        assert result.status == ExecutionStatus.SUCCESS
        assert mock_keyboard.press.call_count >= 3
        assert mock_keyboard.release.call_count >= 3

    def test_keyboard_execution_failure(self) -> None:
        """Test that keyboard execution failures are handled gracefully."""
        action = keyboard_action("invalid_key_that_does_not_exist")

        mock_keyboard = MagicMock()
        with patch(
            "mouseflow.runner._create_keyboard_controller",
            return_value=mock_keyboard,
        ):
            result = run_action(action)

        assert result.status == ExecutionStatus.FAILURE
        assert result.error_message is not None
        assert "Unknown key" in result.error_message

    def test_modifier_keys_recognized(self) -> None:
        """Test that common modifier keys are recognized."""
        action = keyboard_action("alt+left")

        mock_keyboard = MagicMock()
        with (
            patch(
                "mouseflow.runner._create_keyboard_controller",
                return_value=mock_keyboard,
            ),
            patch("mouseflow.runner._get_key") as mock_get_key,
        ):
            mock_get_key.side_effect = lambda k: f"key_{k}"
            result = run_action(action)

        assert result.status == ExecutionStatus.SUCCESS

    def test_single_key_execution(self) -> None:
        """Test that a single key is executed correctly."""
        action = keyboard_action("a")

        mock_keyboard = MagicMock()
        with patch(
            "mouseflow.runner._create_keyboard_controller",
            return_value=mock_keyboard,
        ):
            result = run_action(action)

        assert result.status == ExecutionStatus.SUCCESS
        assert mock_keyboard.press.call_count == 1
        assert mock_keyboard.release.call_count == 1


class TestCommandExecution:
    def test_command_executed_successfully(self) -> None:
        """Test that a shell command is executed successfully."""
        from mouseflow.domain import command_action

        action = command_action("echo 'test'")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = run_action(action)

            assert result.status == ExecutionStatus.SUCCESS
            assert result.action == action
            mock_run.assert_called_once()

    def test_command_with_arguments(self) -> None:
        """Test that a command with arguments is executed correctly."""
        from mouseflow.domain import command_action

        action = command_action("swaymsg workspace next")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = run_action(action)

            assert result.status == ExecutionStatus.SUCCESS
            # Verify the command was passed to subprocess
            call_args = mock_run.call_args
            assert call_args[0][0] == "swaymsg workspace next"

    def test_command_execution_failure(self) -> None:
        """Test that command execution failures are handled gracefully."""
        from mouseflow.domain import command_action

        action = command_action("nonexistent_command_12345")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=127,
                stderr="command not found",
            )

            result = run_action(action)

            assert result.status == ExecutionStatus.FAILURE
            assert result.error_message is not None

    def test_command_timeout(self) -> None:
        """Test that command timeout is handled gracefully."""
        from mouseflow.domain import command_action

        action = command_action("sleep 100")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd="sleep 100",
                timeout=10,
            )

            result = run_action(action)

            assert result.status == ExecutionStatus.FAILURE
            assert result.error_message is not None
            assert "timed out" in result.error_message.lower()


class TestExecutionResultReporting:
    def test_successful_execution_reported(self) -> None:
        """Test that successful execution is reported correctly."""
        action = keyboard_action("ctrl+c")
        result = ExecutionResult(action=action, status=ExecutionStatus.SUCCESS)

        report = format_execution_result(result)

        assert "ctrl+c" in report
        assert "Executed" in report

    def test_failed_execution_reported(self) -> None:
        """Test that failed execution is reported with error details."""
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
        """Test that execution failure does not terminate the application."""
        action = keyboard_action("invalid_key")

        # Should not raise an exception
        result = run_action(action)

        assert result.status == ExecutionStatus.FAILURE
        assert result.error_message is not None

    def test_repeated_failures_handled_gracefully(self) -> None:
        """Test that repeated failures are handled gracefully."""
        actions = [
            keyboard_action("invalid1"),
            keyboard_action("invalid2"),
            keyboard_action("invalid3"),
        ]

        results = []
        for action in actions:
            result = run_action(action)
            results.append(result)

        # All should fail gracefully
        assert len(results) == 3
        for result in results:
            assert result.status == ExecutionStatus.FAILURE
            assert result.error_message is not None


class TestActionTypeDispatch:
    def test_keyboard_action_dispatched(self) -> None:
        """Test that keyboard actions are dispatched correctly."""
        action = keyboard_action("a")

        mock_keyboard = MagicMock()
        with patch(
            "mouseflow.runner._create_keyboard_controller",
            return_value=mock_keyboard,
        ):
            result = run_action(action)

            assert result.status == ExecutionStatus.SUCCESS

    def test_command_action_dispatched(self) -> None:
        """Test that command actions are dispatched correctly."""
        from mouseflow.domain import command_action

        action = command_action("echo test")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = run_action(action)

            assert result.status == ExecutionStatus.SUCCESS

    def test_unknown_action_type(self) -> None:
        """Test that unknown action types are handled gracefully."""
        action = Action(action_type="UNKNOWN", payload="test")  # type: ignore

        result = run_action(action)

        assert result.status == ExecutionStatus.FAILURE
        assert result.error_message is not None
        assert "Unknown action type" in result.error_message


class TestPipelineIntegration:
    def test_full_pipeline_with_keyboard_action(self) -> None:
        """Test full pipeline integration with keyboard action."""
        from mouseflow.domain import (
            Action,
            ActionType,
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

        # Setup configuration
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

        # Create dispatch context
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        # Resolve action
        action = resolve_action(context, config)
        assert action is not None

        # Execute action
        mock_keyboard = MagicMock()
        with patch(
            "mouseflow.runner._create_keyboard_controller",
            return_value=mock_keyboard,
        ):
            result = run_action(action)

            assert result.status == ExecutionStatus.SUCCESS
            assert result.action.payload == "alt+left"

    def test_full_pipeline_with_shell_command(self) -> None:
        """Test full pipeline integration with shell command."""
        from mouseflow.domain import (
            Action,
            ActionType,
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

        # Setup configuration
        config = Configuration(
            profiles=(
                Profile(
                    app_name="terminal",
                    mappings={
                        "BTN_EXTRA": Action(
                            action_type=ActionType.COMMAND,
                            payload="echo 'test'",
                        ),
                    },
                ),
            ),
        )

        # Create dispatch context
        event = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        window_info = WindowInfo(
            application=Application(app_name="terminal"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        # Resolve action
        action = resolve_action(context, config)
        assert action is not None

        # Execute action
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = run_action(action)

            assert result.status == ExecutionStatus.SUCCESS
            assert result.action.payload == "echo 'test'"

    def test_full_pipeline_with_application_launch(self) -> None:
        """Test full pipeline integration with application launch."""
        from mouseflow.domain import (
            Action,
            ActionType,
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

        # Setup configuration
        config = Configuration(
            profiles=(
                Profile(
                    app_name="desktop",
                    mappings={
                        "BTN_FORWARD": Action(
                            action_type=ActionType.COMMAND,
                            payload="firefox",
                        ),
                    },
                ),
            ),
        )

        # Create dispatch context
        event = MouseEvent.button_event(MouseButton.BTN_FORWARD)
        window_info = WindowInfo(
            application=Application(app_name="desktop"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        # Resolve action
        action = resolve_action(context, config)
        assert action is not None

        # Execute action
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = run_action(action)

            assert result.status == ExecutionStatus.SUCCESS
            assert result.action.payload == "firefox"

    def test_pipeline_with_mixed_action_types(self) -> None:
        """Test pipeline with mixed action types."""
        from mouseflow.domain import (
            Action,
            ActionType,
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

        # Setup configuration with multiple action types
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": Action(
                            action_type=ActionType.KEYBOARD,
                            payload="alt+left",
                        ),
                        "BTN_EXTRA": Action(
                            action_type=ActionType.COMMAND,
                            payload="echo 'test'",
                        ),
                    },
                ),
            ),
        )

        # Test keyboard action
        event1 = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context1 = DispatchContext(event=event1, window_info=window_info)

        action1 = resolve_action(context1, config)
        assert action1 is not None

        mock_keyboard = MagicMock()
        with patch(
            "mouseflow.runner._create_keyboard_controller",
            return_value=mock_keyboard,
        ):
            result1 = run_action(action1)
            assert result1.status == ExecutionStatus.SUCCESS

        # Test command action
        event2 = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        context2 = DispatchContext(event=event2, window_info=window_info)

        action2 = resolve_action(context2, config)
        assert action2 is not None

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result2 = run_action(action2)
            assert result2.status == ExecutionStatus.SUCCESS

    def test_pipeline_resilience_with_simulated_failures(self) -> None:
        """Test pipeline resilience with simulated failures."""
        from mouseflow.domain import (
            Action,
            ActionType,
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

        # Setup configuration
        config = Configuration(
            profiles=(
                Profile(
                    app_name="firefox",
                    mappings={
                        "BTN_SIDE": Action(
                            action_type=ActionType.COMMAND,
                            payload="nonexistent_command",
                        ),
                    },
                ),
            ),
        )

        # Create dispatch context
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        window_info = WindowInfo(
            application=Application(app_name="firefox"),
            window=Window(title="Test"),
        )
        context = DispatchContext(event=event, window_info=window_info)

        # Resolve action
        action = resolve_action(context, config)
        assert action is not None

        # Execute action with simulated failure
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=127,
                stderr="command not found",
            )

            result = run_action(action)

            # Should fail gracefully
            assert result.status == ExecutionStatus.FAILURE
            assert result.error_message is not None

        # Pipeline should still be able to process next event
        action2 = resolve_action(context, config)
        assert action2 is not None

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result2 = run_action(action2)
            assert result2.status == ExecutionStatus.SUCCESS
