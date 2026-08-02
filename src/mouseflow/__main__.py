import sys

from mouseflow.discovery import find_supported_device, format_found, format_not_found
from mouseflow.dispatcher import EventDispatcher, format_dispatch_context
from mouseflow.engine import read_events
from mouseflow.resolver import SwayResolver


def main() -> None:
    device = find_supported_device()
    if device is not None:
        print(format_found(device))

        resolver = SwayResolver()
        dispatcher = EventDispatcher(resolver)

        for context in dispatcher.dispatch(read_events(device.path)):
            print(format_dispatch_context(context))
    else:
        print(format_not_found())
        sys.exit(1)


if __name__ == "__main__":
    main()
