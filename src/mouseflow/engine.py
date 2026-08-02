from __future__ import annotations

import signal
import sys
from collections.abc import Generator
from typing import TYPE_CHECKING

from evdev import InputDevice, ecodes

from mouseflow.domain import (
    EventType,
    Gesture,
    MouseButton,
    MouseEvent,
    WheelAxis,
)
from mouseflow.gesture import GestureRecognizer

if TYPE_CHECKING:
    from evdev import InputEvent

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
        print(f"Error: Cannot open device {path}: {e}", file=sys.stderr)
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


def read_events(device_path: str) -> Generator[MouseEvent]:
    """Read mouse events from device (legacy, button/wheel only)."""
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
                    yield domain_event
    except OSError:
        print("Error: Device disconnected or unavailable", file=sys.stderr)
        device.close()
        raise


def read_events_with_gestures(
    device_path: str,
) -> Generator[MouseEvent | Gesture]:
    """Read mouse events with gesture recognition.

    This generator yields both MouseEvent objects (for button/wheel events)
    and Gesture objects (when a directional gesture is recognized).

    Args:
        device_path: Path to the input device.

    Yields:
        MouseEvent or Gesture objects as they occur.
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

            # Check for movement events (REL_X, REL_Y)
            movement = to_movement_delta(event)
            if movement is not None:
                delta_x, delta_y = movement
                recognizer.process_movement(delta_x, delta_y)
                continue

            # Convert to domain event
            domain_event = to_domain_event(event)
            if domain_event is None:
                continue

            # Check if this is the gesture button
            is_gesture_button = domain_event.button == recognizer._gesture_button

            # Process through gesture recognizer
            gesture = recognizer.process_event(domain_event)
            if gesture is not None:
                yield gesture
            elif not is_gesture_button:
                # Only yield non-gesture button events
                yield domain_event
    except OSError:
        print("Error: Device disconnected or unavailable", file=sys.stderr)
        device.close()
        raise


def run_engine(device_path: str) -> None:
    try:
        for domain_event in read_events(device_path):
            if domain_event.event_type == EventType.BUTTON:
                button = domain_event.button
                button_val = button.value if button else "UNKNOWN"
                print(button_val)
            elif domain_event.event_type == EventType.WHEEL:
                wheel = domain_event.wheel
                wheel_val = wheel.value if wheel else "UNKNOWN"
                print(wheel_val)
    except OSError:
        sys.exit(1)
