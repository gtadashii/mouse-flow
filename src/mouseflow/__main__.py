import sys

from mouseflow.discovery import find_supported_device, format_found, format_not_found
from mouseflow.engine import run_engine


def main() -> None:
    device = find_supported_device()
    if device is not None:
        print(format_found(device))
        run_engine(device.path)
    else:
        print(format_not_found())
        sys.exit(1)


if __name__ == "__main__":
    main()
