from __future__ import annotations

import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from mouseflow.domain import (
    Action,
    ActionExecutor,
    ActionType,
    ExecutionResult,
    ExecutionStatus,
)


class KeyboardController(Protocol):
    def press(self, key: Any) -> None: ...
    def release(self, key: Any) -> None: ...


def _create_keyboard_controller() -> KeyboardController:
    from pynput.keyboard import Controller

    controller: KeyboardController = Controller()
    return controller


@dataclass(frozen=True)
class KeyboardAdapter:
    controller: KeyboardController
    key_map: Mapping[str, object]

    @classmethod
    def create_default(cls) -> KeyboardAdapter:
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
        return cls(controller=_create_keyboard_controller(), key_map=key_map)

    def execute(self, action: Action) -> ExecutionResult:
        try:
            key_names = self._parse_key_combination(action.payload)
            keys = self._to_pynput_keys(key_names)

            for key in keys[:-1]:
                self.controller.press(key)

            self.controller.press(keys[-1])
            self.controller.release(keys[-1])

            for key in reversed(keys[:-1]):
                self.controller.release(key)

            return ExecutionResult(action=action, status=ExecutionStatus.SUCCESS)
        except Exception as e:
            return ExecutionResult(
                action=action,
                status=ExecutionStatus.FAILURE,
                error_message=str(e),
            )

    def _parse_key_combination(self, keys_str: str) -> list[str]:
        parts = keys_str.lower().split("+")
        return [part.strip() for part in parts]

    def _to_pynput_keys(self, key_names: list[str]) -> list[object]:
        keys = []
        for name in key_names:
            key = self.key_map.get(name)
            if key is not None:
                keys.append(key)
            elif len(name) == 1:
                keys.append(name)
            else:
                raise ValueError(f"Unknown key: {name}")

        return keys


@dataclass(frozen=True)
class ShellAdapter:
    timeout: int = 10

    def execute(self, action: Action) -> ExecutionResult:
        try:
            result = subprocess.run(
                action.payload,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
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


@dataclass(frozen=True)
class ActionRunner:
    executors: Mapping[ActionType, ActionExecutor]

    @classmethod
    def create_default(cls) -> ActionRunner:
        keyboard_adapter = KeyboardAdapter.create_default()
        shell_adapter = ShellAdapter()

        executors: dict[ActionType, ActionExecutor] = {
            ActionType.KEYBOARD: keyboard_adapter,
            ActionType.COMMAND: shell_adapter,
        }
        return cls(executors=executors)

    def run(self, action: Action) -> ExecutionResult:
        executor = self.executors.get(action.action_type)
        if executor is None:
            return ExecutionResult(
                action=action,
                status=ExecutionStatus.FAILURE,
                error_message=f"Unknown action type: {action.action_type}",
            )
        return executor.execute(action)


_default_runner: ActionRunner | None = None


def _get_default_runner() -> ActionRunner:
    global _default_runner
    if _default_runner is None:
        _default_runner = ActionRunner.create_default()
    return _default_runner


def run_action(action: Action) -> ExecutionResult:
    return _get_default_runner().run(action)


def format_execution_result(result: ExecutionResult) -> str:
    if result.status == ExecutionStatus.SUCCESS:
        return f"Action: {result.action.payload}\nStatus: Executed"
    error_msg = result.error_message or "Unknown error"
    return f"Action: {result.action.payload}\nStatus: Failed\nError: {error_msg}"
