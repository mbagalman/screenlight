from __future__ import annotations

import json
import socket
import sys
import threading
from typing import Dict

from .backends import OverlayBackend
from .config import WIDTH_TO_PIXELS
from .ipc import HOST, PORT


class UnsupportedPlatformError(RuntimeError):
    pass


def select_backend_class(platform: str | None = None) -> type[OverlayBackend]:
    resolved = platform or sys.platform
    if resolved.startswith("win"):
        from .backends.windows_backend import WindowsOverlayBackend

        return WindowsOverlayBackend
    if resolved == "darwin":
        from .backends.macos_backend import MacOSOverlayBackend, get_macos_support_error

        support_error = get_macos_support_error()
        if support_error:
            raise UnsupportedPlatformError(support_error)
        return MacOSOverlayBackend
    raise UnsupportedPlatformError(
        f"screenlight: unsupported platform '{resolved}'. "
        "Current release supports Windows only."
    )


def handle_control_message(
    message: Dict[str, object], backend: OverlayBackend
) -> Dict[str, object]:
    command = message.get("command")

    if command == "ping":
        return {"ok": True}

    if command == "off":
        backend.shutdown()
        return {"ok": True}

    if command == "update":
        width_name = message.get("width")
        brightness = message.get("brightness")
        if (
            isinstance(width_name, str)
            and width_name in WIDTH_TO_PIXELS
            and isinstance(brightness, int)
            and 1 <= brightness <= 10
        ):
            backend.update(width_name, brightness)
            return {"ok": True}
        return {"ok": False, "error": "invalid payload"}

    return {"ok": False, "error": "unknown command"}


class OverlayServiceManager:
    def __init__(self, width_name: str, brightness: int) -> None:
        self._stopped = threading.Event()
        self._backend = self._create_backend(width_name, brightness)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind((HOST, PORT))
            self.sock.listen(5)
            self.sock.settimeout(0.5)
        except OSError as exc:
            self.sock.close()
            raise RuntimeError(f"Unable to bind control port {PORT}.") from exc

        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)

    def _create_backend(self, width_name: str, brightness: int) -> OverlayBackend:
        backend_class = select_backend_class()
        return backend_class(
            width_name=width_name,
            brightness=brightness,
            on_shutdown=self._signal_stop,
        )

    def _signal_stop(self) -> None:
        if self._stopped.is_set():
            return
        self._stopped.set()
        try:
            self.sock.close()
        except OSError:
            pass

    def _handle_message(self, message: Dict[str, object]) -> Dict[str, object]:
        return handle_control_message(message=message, backend=self._backend)

    def _server_loop(self) -> None:
        while not self._stopped.is_set():
            try:
                conn, _addr = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            with conn:
                try:
                    raw = b""
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        raw += chunk

                    payload = json.loads(raw.decode("utf-8").strip() or "{}")
                    response = self._handle_message(payload)
                except Exception:
                    response = {"ok": False, "error": "bad request"}

                try:
                    conn.sendall(json.dumps(response).encode("utf-8"))
                except OSError:
                    pass

    def run(self) -> None:
        self.server_thread.start()
        try:
            self._backend.run()
        finally:
            self._signal_stop()


def ensure_platform_supported() -> None:
    select_backend_class()


def run_service(width_name: str, brightness: int) -> None:
    service = OverlayServiceManager(width_name=width_name, brightness=brightness)
    service.run()
