import sys

from mouseflow.discovery import find_supported_device, format_found, format_not_found
from mouseflow.dispatcher import EventDispatcher, format_dispatch_context
from mouseflow.engine import read_events
from mouseflow.loader import resolve_action
from mouseflow.parser import parse_config
from mouseflow.profile_resolver import DefaultProfileResolver
from mouseflow.resolver import SwayResolver
from mouseflow.runner import format_execution_result, run_action


def main() -> None:
    device = find_supported_device()
    if device is None:
        print(format_not_found())
        sys.exit(1)

    print(format_found(device))

    config = parse_config()
    resolver = SwayResolver()
    dispatcher = EventDispatcher(resolver)
    profile_resolver = DefaultProfileResolver()

    for context in dispatcher.dispatch(read_events(device.path)):
        profile = profile_resolver.resolve(config, context.window_info)
        print(format_dispatch_context(context, profile))

        action = resolve_action(context, profile)
        if action is not None:
            result = run_action(action)
            print(format_execution_result(result))
        else:
            print("Action: None")


if __name__ == "__main__":
    main()
