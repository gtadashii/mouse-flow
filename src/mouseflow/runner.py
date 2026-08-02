from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from mouseflow.domain import Action, ActionType


class ExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass(frozen=True)
class ExecutionResult:
    action: Action
    status: ExecutionStatus
    error_message: str | None = None


class KeyboardController(Protocol):
    def press(self, key: Any) -> None: ...
    def release(self, key: Any) -> None: ...


def _create_keyboard_controller() -> KeyboardController:
    from pynput.keyboard import Controller

    controller: KeyboardController = Controller()
    return controller


def _get_key(name: str) -> Any:
    from pynput.keyboard import Key

    key_map = {
        "ctrl": Key.ctrl,
        "alt": Key.alt,
        "shift": Key.shift,
        "super": Key.cmd,
        "cmd": Key.cmd,
        "win": Key.cmd,
        "enter": Key.enter,
        "tab": Key.tab,
        "space": Key.space,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "escape": Key.esc,
        "esc": Key.esc,
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "home": Key.home,
        "end": Key.end,
        "pageup": Key.page_up,
        "pagedown": Key.page_down,
        "f1": Key.f1,
        "f2": Key.f2,
        "f3": Key.f3,
        "f4": Key.f4,
        "f5": Key.f5,
        "f6": Key.f6,
        "f7": Key.f7,
        "f8": Key.f8,
        "f9": Key.f9,
        "f10": Key.f10,
        "f11": Key.f11,
        "f12": Key.f12,
    }
    return key_map.get(name)


def run_action(action: Action) -> ExecutionResult:
    """Execute an action and return the result."""
    if action.action_type == ActionType.KEYBOARD:
        return _execute_keyboard(action)
    if action.action_type == ActionType.COMMAND:
        return _execute_command(action)
    return ExecutionResult(
        action=action,
        status=ExecutionStatus.FAILURE,
        error_message=f"Unknown action type: {action.action_type}",
    )


def _execute_keyboard(action: Action) -> ExecutionResult:
    """Execute a keyboard shortcut action."""
    try:
        keyboard = _create_keyboard_controller()
        keys = _parse_key_combination(action.payload)

        for key in keys[:-1]:
            keyboard.press(key)

        keyboard.press(keys[-1])
        keyboard.release(keys[-1])

        for key in reversed(keys[:-1]):
            keyboard.release(key)

        return ExecutionResult(action=action, status=ExecutionStatus.SUCCESS)
    except Exception as e:
        return ExecutionResult(
            action=action,
            status=ExecutionStatus.FAILURE,
            error_message=str(e),
        )


def _execute_command(action: Action) -> ExecutionResult:
    """Execute a shell command action."""
    try:
        import subprocess

        result = subprocess.run(
            action.payload,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return ExecutionResult(action=action, status=ExecutionStatus.SUCCESS)
        error_msg = (
            result.stderr or f"Command failed with return code {result.returncode}"
        )
        return ExecutionResult(
            action=action,
            status=ExecutionStatus.FAILURE,
            error_message=error_msg,
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            action=action,
            status=ExecutionStatus.FAILURE,
            error_message="Command timed out",
        )
    except Exception as e:
        return ExecutionResult(
            action=action,
            status=ExecutionStatus.FAILURE,
            error_message=str(e),
        )


def _parse_key_combination(keys_str: str) -> list[object]:
    """Parse a key combination string like 'ctrl+shift+p' into pynput keys."""
    parts = keys_str.lower().split("+")
    keys = []

    for part in parts:
        part = part.strip()
        key = _get_key(part)
        if key is not None:
            keys.append(key)
        elif len(part) == 1:
            keys.append(part)
        else:
            raise ValueError(f"Unknown key: {part}")

    return keys


def format_execution_result(result: ExecutionResult) -> str:
    """Format an execution result for display."""
    if result.status == ExecutionStatus.SUCCESS:
        return f"Action: {result.action.payload}\nStatus: Executed"
    error_msg = result.error_message or "Unknown error"
    return f"Action: {result.action.payload}\nStatus: Failed\nError: {error_msg}"
