import sys

from mouseflow.discovery import find_supported_device, format_found, format_not_found
from mouseflow.engine import read_events
from mouseflow.resolver import format_window_info, resolve_active_window


def main() -> None:
    device = find_supported_device()
    if device is not None:
        print(format_found(device))
        window_info = resolve_active_window()
        if window_info is not None:
            print(format_window_info(window_info))
        for event in read_events(device.path):
            if event.event_type.value == "BUTTON":
                button = event.button
                print(button.value if button else "UNKNOWN")
            elif event.event_type.value == "WHEEL":
                wheel = event.wheel
                print(wheel.value if wheel else "UNKNOWN")
    else:
        print(format_not_found())
        sys.exit(1)


if __name__ == "__main__":
    main()
