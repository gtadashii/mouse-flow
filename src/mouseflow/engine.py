from __future__ import annotations

import logging
import signal
import sys
from collections.abc import Generator
from typing import TYPE_CHECKING

from evdev import InputDevice, ecodes

from mouseflow.domain import (
    EventType,
    Gesture,
    GestureDirection,
    InputIdentifier,
    MouseButton,
    MouseEvent,
    UserInput,
    WheelAxis,
)
from mouseflow.gesture import GestureRecognizer

if TYPE_CHECKING:
    from evdev import InputEvent

logger = logging.getLogger(__name__)

SUPPORTED_EVENTS: dict[int, set[int]] = {
    ecodes.EV_KEY: {
        ecodes.BTN_SIDE,
        ecodes.BTN_EXTRA,
        ecodes.BTN_FORWARD,
    },
    ecodes.EV_REL: {
        ecodes.REL_HWHEEL,
        ecodes.REL_X,
        ecodes.REL_Y,
    },
}


def open_device(path: str) -> InputDevice[str]:
    try:
        return InputDevice(path)
    except (OSError, FileNotFoundError) as e:
        logger.error("Cannot open device %s: %s", path, e)
        sys.exit(1)


def is_supported_event(event: InputEvent) -> bool:
    event_type = event.type
    event_code = event.code

    if event_type not in SUPPORTED_EVENTS:
        return False

    return event_code in SUPPORTED_EVENTS[event_type]


def get_event_name(event: InputEvent) -> str:
    event_type = event.type
    event_code = event.code

    if event_type == ecodes.EV_KEY:
        result = ecodes.BTN.get(event_code, f"UNKNOWN_KEY_{event_code}")
        return result if isinstance(result, str) else result[0]
    if event_type == ecodes.EV_REL:
        result = ecodes.REL.get(event_code, f"UNKNOWN_REL_{event_code}")
        return result if isinstance(result, str) else result[0]
    return f"UNKNOWN_{event_type}_{event_code}"


def to_domain_event(event: InputEvent) -> MouseEvent | None:
    event_type = event.type
    event_code = event.code

    if event_type == ecodes.EV_KEY:
        button_map = {
            ecodes.BTN_SIDE: MouseButton.BTN_SIDE,
            ecodes.BTN_EXTRA: MouseButton.BTN_EXTRA,
            ecodes.BTN_FORWARD: MouseButton.BTN_FORWARD,
        }
        button = button_map.get(event_code)
        if button is None:
            return None
        return MouseEvent.button_event(button, pressed=event.value == 1)

    if event_type == ecodes.EV_REL:
        axis_map = {
            ecodes.REL_HWHEEL: WheelAxis.REL_HWHEEL,
        }
        axis = axis_map.get(event_code)
        if axis is None:
            return None
        return MouseEvent.wheel_event(axis, event.value)

    return None


def to_movement_delta(event: InputEvent) -> tuple[int, int] | None:
    """Convert REL_X/REL_Y event to movement delta.

    Args:
        event: The input event.

    Returns:
        Tuple of (delta_x, delta_y) if event is a movement event, None otherwise.
    """
    if event.type == ecodes.EV_REL:
        if event.code == ecodes.REL_X:
            return (event.value, 0)
        if event.code == ecodes.REL_Y:
            return (0, event.value)
    return None


def mouse_event_to_userinput(event: MouseEvent) -> UserInput:
    """Convert internal MouseEvent to UserInput for pipeline consumption."""
    if event.event_type == EventType.BUTTON:
        if event.button is None:
            raise ValueError("Button event must have a button")
        button_to_identifier = {
            MouseButton.BTN_SIDE: InputIdentifier.BTN_SIDE,
            MouseButton.BTN_EXTRA: InputIdentifier.BTN_EXTRA,
            MouseButton.BTN_FORWARD: InputIdentifier.BTN_FORWARD,
            MouseButton.BTN_BACK: InputIdentifier.BTN_BACK,
        }
        identifier = button_to_identifier.get(event.button)
        if identifier is None:
            raise ValueError(f"Unknown button: {event.button}")
        return UserInput(identifier=identifier)

    if event.event_type == EventType.WHEEL:
        if event.wheel is None:
            raise ValueError("Wheel event must have a wheel axis")
        if event.wheel == WheelAxis.REL_HWHEEL:
            if event.value > 0:
                return UserInput(identifier=InputIdentifier.THUMB_WHEEL_RIGHT)
            if event.value < 0:
                return UserInput(identifier=InputIdentifier.THUMB_WHEEL_LEFT)
        raise ValueError(f"Unsupported wheel axis: {event.wheel}")

    raise ValueError(f"Unknown event type: {event.event_type}")


def gesture_to_userinput(gesture: Gesture) -> UserInput:
    """Convert internal Gesture to UserInput for pipeline consumption."""
    direction_to_identifier = {
        GestureDirection.UP: InputIdentifier.GESTURE_UP,
        GestureDirection.DOWN: InputIdentifier.GESTURE_DOWN,
        GestureDirection.LEFT: InputIdentifier.GESTURE_LEFT,
        GestureDirection.RIGHT: InputIdentifier.GESTURE_RIGHT,
    }
    identifier = direction_to_identifier.get(gesture.direction)
    if identifier is None:
        raise ValueError(f"Unknown gesture direction: {gesture.direction}")
    return UserInput(identifier=identifier)


def read_events(device_path: str) -> Generator[UserInput]:
    """Read mouse events from device and convert to UserInput."""
    device = open_device(device_path)

    def signal_handler(_signum: int, _frame: object) -> None:
        device.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        for event in device.read_loop():
            if is_supported_event(event):
                domain_event = to_domain_event(event)
                if domain_event is not None:
                    yield mouse_event_to_userinput(domain_event)
    except OSError:
        logger.error("Device disconnected or unavailable")
        device.close()
        raise


def read_events_with_gestures(
    device_path: str,
) -> Generator[UserInput]:
    """Read mouse events with gesture recognition.

    This generator yields UserInput objects for both button/wheel events
    and recognized gestures.

    Args:
        device_path: Path to the input device.

    Yields:
        UserInput objects as they occur.
    """
    device = open_device(device_path)
    recognizer = GestureRecognizer()

    def signal_handler(_signum: int, _frame: object) -> None:
        device.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        for event in device.read_loop():
            if not is_supported_event(event):
                continue

            movement = to_movement_delta(event)
            if movement is not None:
                delta_x, delta_y = movement
                recognizer.process_movement(delta_x, delta_y)
                continue

            domain_event = to_domain_event(event)
            if domain_event is None:
                continue

            is_gesture_button = domain_event.button == recognizer._gesture_button

            gesture = recognizer.process_event(domain_event)
            if gesture is not None:
                yield gesture_to_userinput(gesture)
            elif not is_gesture_button:
                yield mouse_event_to_userinput(domain_event)
    except OSError:
        logger.error("Device disconnected or unavailable")
        device.close()
        raise


def run_engine(device_path: str) -> None:
    try:
        for user_input in read_events(device_path):
            print(user_input.identifier.value)
    except OSError:
        sys.exit(1)
