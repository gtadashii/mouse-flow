from __future__ import annotations

import signal
import sys
from typing import TYPE_CHECKING

from evdev import InputDevice, ecodes

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


def run_engine(device_path: str) -> None:
    device = open_device(device_path)

    def signal_handler(_signum: int, _frame: object) -> None:
        device.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        for event in device.read_loop():
            if is_supported_event(event):
                event_name = get_event_name(event)
                print(event_name)
    except OSError:
        print("Error: Device disconnected or unavailable", file=sys.stderr)
        device.close()
        sys.exit(1)
