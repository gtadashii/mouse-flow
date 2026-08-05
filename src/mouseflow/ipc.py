from __future__ import annotations

import contextlib
import json
import logging
import socket
import threading
from dataclasses import asdict
from pathlib import Path
from typing import Any

from mouseflow.domain import (
    Configuration,
    DeviceInfo,
)
from mouseflow.services import ApplicationServices

logger = logging.getLogger(__name__)

DEFAULT_SOCKET_PATH = Path.home() / ".local" / "state" / "mouseflow" / "mouseflow.sock"


class IPCError(Exception):
    pass


class IPCConnectionError(IPCError):
    pass


def _serialize_device_info(devices: list[DeviceInfo]) -> list[dict[str, Any]]:
    return [asdict(d) for d in devices]


def _serialize_configuration(config: Configuration | None) -> dict[str, Any] | None:
    if config is None:
        return None
    profiles = []
    for profile in config.profiles:
        mappings = {}
        for input_id, action in profile.mappings.items():
            mappings[input_id.value] = {
                "type": action.action_type.value.lower(),
                "payload": action.payload,
            }
        profiles.append(
            {
                "app_name": profile.app_name,
                "mappings": mappings,
            }
        )
    return {"profiles": profiles}


def _serialize_result(result: Any) -> dict[str, Any]:
    if hasattr(result, "__dataclass_fields__"):
        return asdict(result)
    return {}


class IPCServer:
    def __init__(
        self,
        services: ApplicationServices,
        socket_path: Path | None = None,
    ) -> None:
        self._services = services
        self._socket_path = socket_path or DEFAULT_SOCKET_PATH
        self._server_socket: socket.socket | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._socket_path.parent.mkdir(parents=True, exist_ok=True)
        if self._socket_path.exists():
            self._socket_path.unlink()

        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_socket.bind(str(self._socket_path))
        self._server_socket.listen(5)
        self._server_socket.settimeout(1.0)
        self._running = True

        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        logger.info("IPC server started on %s", self._socket_path)

    def stop(self) -> None:
        self._running = False
        if self._server_socket is not None:
            with contextlib.suppress(OSError):
                self._server_socket.close()
            self._server_socket = None
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
        if self._socket_path.exists():
            with contextlib.suppress(OSError):
                self._socket_path.unlink()
        logger.info("IPC server stopped")

    def _accept_loop(self) -> None:
        while self._running:
            try:
                conn, _ = self._server_socket.accept()  # type: ignore[union-attr]
                threading.Thread(
                    target=self._handle_connection,
                    args=(conn,),
                    daemon=True,
                ).start()
            except TimeoutError:
                continue
            except OSError:
                if self._running:
                    logger.exception("IPC accept error")
                break

    def _handle_connection(self, conn: socket.socket) -> None:
        try:
            data = conn.recv(4096)
            if not data:
                return
            request = json.loads(data)
            response = self._dispatch(request)
            conn.sendall(json.dumps(response).encode())
        except json.JSONDecodeError:
            response = {"status": "error", "message": "Invalid JSON"}
            with contextlib.suppress(OSError):
                conn.sendall(json.dumps(response).encode())
        except Exception:
            logger.exception("IPC handler error")
            response = {"status": "error", "message": "Internal server error"}
            with contextlib.suppress(OSError):
                conn.sendall(json.dumps(response).encode())
        finally:
            conn.close()

    def _dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        command = request.get("command")
        args = request.get("args", {})

        handlers: dict[str, Any] = {
            "devices": self._handle_devices,
            "status": self._handle_status,
            "config_show": self._handle_config_show,
            "config_validate": self._handle_config_validate,
            "config_reload": self._handle_config_reload,
        }

        handler = handlers.get(command)  # type: ignore[arg-type]
        if handler is None:
            return {"status": "error", "message": f"Unknown command: {command}"}

        try:
            result = handler(args)
            return {"status": "ok", "data": result}
        except Exception as e:
            logger.exception("Command '%s' failed", command)
            return {"status": "error", "message": str(e)}

    def _handle_devices(self, _args: dict[str, Any]) -> list[dict[str, Any]]:
        devices = self._services.list_devices()
        return _serialize_device_info(devices)

    def _handle_status(self, _args: dict[str, Any]) -> dict[str, Any]:
        status = self._services.get_status()
        return _serialize_result(status)

    def _handle_config_show(self, _args: dict[str, Any]) -> dict[str, Any] | None:
        config = self._services.get_configuration()
        return _serialize_configuration(config)

    def _handle_config_validate(self, args: dict[str, Any]) -> dict[str, Any]:
        path_str = args.get("path")
        path = Path(path_str) if path_str else None
        result = self._services.validate_configuration(path)
        return _serialize_result(result)

    def _handle_config_reload(self, _args: dict[str, Any]) -> dict[str, Any]:
        result = self._services.reload_configuration()
        return _serialize_result(result)


class IPCClient:
    def __init__(self, socket_path: Path | None = None) -> None:
        self._socket_path = socket_path or DEFAULT_SOCKET_PATH

    def send_command(
        self,
        command: str,
        args: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self._socket_path.exists():
            raise IPCConnectionError("Daemon not running (socket not found)")

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(str(self._socket_path))
            request = {"command": command, "args": args or {}}
            sock.sendall(json.dumps(request).encode())

            data = sock.recv(65536)
            if not data:
                raise IPCConnectionError("No response from daemon")
            return json.loads(data)  # type: ignore[no-any-return]
        except ConnectionRefusedError as e:
            raise IPCConnectionError("Daemon not running (connection refused)") from e
        except FileNotFoundError as e:
            raise IPCConnectionError("Daemon not running (socket not found)") from e
        finally:
            sock.close()
