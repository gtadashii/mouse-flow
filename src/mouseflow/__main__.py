import sys

from mouseflow.daemon import Daemon, DaemonError, DaemonInitializationError


def main() -> None:
    try:
        daemon = Daemon()
        daemon.run()
    except DaemonInitializationError as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)
    except DaemonError as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
