from mouseflow.daemon import Daemon


def main() -> None:
    daemon = Daemon()
    daemon.run()


if __name__ == "__main__":
    main()
