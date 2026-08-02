from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

GLOBAL_PROFILE_NAME = "global"


class ExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class InputIdentifier(Enum):
    BTN_SIDE = "BTN_SIDE"
    BTN_EXTRA = "BTN_EXTRA"
    BTN_FORWARD = "BTN_FORWARD"
    BTN_BACK = "BTN_BACK"
    GESTURE_UP = "GESTURE_UP"
    GESTURE_DOWN = "GESTURE_DOWN"
    GESTURE_LEFT = "GESTURE_LEFT"
    GESTURE_RIGHT = "GESTURE_RIGHT"


class MouseButton(Enum):
    BTN_SIDE = "BTN_SIDE"
    BTN_EXTRA = "BTN_EXTRA"
    BTN_FORWARD = "BTN_FORWARD"
    BTN_BACK = "BTN_BACK"


class WheelAxis(Enum):
    REL_HWHEEL = "REL_HWHEEL"
    REL_WHEEL = "REL_WHEEL"


class GestureDirection(Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class EventType(Enum):
    BUTTON = "BUTTON"
    WHEEL = "WHEEL"


@dataclass(frozen=True)
class MouseEvent:
    event_type: EventType
    button: MouseButton | None = None
    wheel: WheelAxis | None = None
    value: int = 0

    @classmethod
    def button_event(cls, button: MouseButton, pressed: bool = True) -> MouseEvent:
        return cls(
            event_type=EventType.BUTTON,
            button=button,
            value=1 if pressed else 0,
        )

    @classmethod
    def wheel_event(cls, axis: WheelAxis, value: int) -> MouseEvent:
        return cls(
            event_type=EventType.WHEEL,
            wheel=axis,
            value=value,
        )


@dataclass(frozen=True)
class Gesture:
    direction: GestureDirection


@dataclass(frozen=True)
class UserInput:
    identifier: InputIdentifier


@dataclass(frozen=True)
class Application:
    app_name: str = "Unknown"


@dataclass(frozen=True)
class Window:
    title: str = "Untitled"


@dataclass(frozen=True)
class WindowInfo:
    application: Application
    window: Window


@dataclass(frozen=True)
class DispatchContext:
    event: UserInput
    window_info: WindowInfo | None = None


class ActionType(Enum):
    KEYBOARD = "KEYBOARD"
    COMMAND = "COMMAND"


@dataclass(frozen=True)
class Action:
    action_type: ActionType
    payload: str


def keyboard_action(keys: str) -> Action:
    return Action(action_type=ActionType.KEYBOARD, payload=keys)


def command_action(cmd: str) -> Action:
    return Action(action_type=ActionType.COMMAND, payload=cmd)


@dataclass(frozen=True)
class Profile:
    app_name: str
    mappings: dict[InputIdentifier, Action] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "mappings", dict(self.mappings))


@dataclass(frozen=True)
class Configuration:
    profiles: tuple[Profile, ...] = ()

    def get_profile(self, app_name: str) -> Profile | None:
        for profile in self.profiles:
            if profile.app_name == app_name:
                return profile
        return None

    def get_global_profile(self) -> Profile | None:
        return self.get_profile(GLOBAL_PROFILE_NAME)


@dataclass(frozen=True)
class ExecutionResult:
    action: Action
    status: ExecutionStatus
    error_message: str | None = None


class ActionExecutor(Protocol):
    def execute(self, action: Action) -> ExecutionResult: ...
