from __future__ import annotations

import signal
import sys
from typing import TYPE_CHECKING

from evdev import InputDevice, ecodes

from mouseflow.domain import EventType, MouseButton, MouseEvent, WheelAxis

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


def run_engine(device_path: str) -> None:
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
                    if domain_event.event_type == EventType.BUTTON:
                        button = domain_event.button
                        button_val = button.value if button else "UNKNOWN"
                        print(button_val)
                    elif domain_event.event_type == EventType.WHEEL:
                        wheel = domain_event.wheel
                        wheel_val = wheel.value if wheel else "UNKNOWN"
                        print(wheel_val)
    except OSError:
        print("Error: Device disconnected or unavailable", file=sys.stderr)
        device.close()
        sys.exit(1)
