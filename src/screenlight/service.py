from __future__ import annotations

import json
import socket
import threading
import tkinter as tk
from typing import Dict

from .config import WIDTH_TO_PIXELS, brightness_to_alpha
from .ipc import HOST, PORT

TRANSPARENT_KEY = "#00FF00"
FADE_STEPS = 8
FADE_STEP_MS = 20


class OverlayService:
    def __init__(self, width_name: str, brightness: int) -> None:
        self.width_name = width_name
        self.brightness = brightness
        self.current_alpha = 0.0
        self.target_alpha = brightness_to_alpha(brightness)
        self.running = True

        self.root = tk.Tk()
        self.root.title("Screenlight")
        self.root.overrideredirect(True)
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT_KEY)

        try:
            self.root.attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError as exc:
            raise RuntimeError(
                "Transparent center not supported on this platform/window manager. "
                "MVP currently targets Windows."
            ) from exc

        self.top = tk.Frame(self.root, bg="white", highlightthickness=0, bd=0)
        self.bottom = tk.Frame(self.root, bg="white", highlightthickness=0, bd=0)
        self.left = tk.Frame(self.root, bg="white", highlightthickness=0, bd=0)
        self.right = tk.Frame(self.root, bg="white", highlightthickness=0, bd=0)

        self._apply_layout()
        self.root.attributes("-alpha", 0.0)

        self.root.bind("<Escape>", lambda _event: self._start_shutdown())
        self.root.after(0, self._fade_in)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind((HOST, PORT))
            self.sock.listen(5)
            self.sock.settimeout(0.5)
        except OSError as exc:
            self.sock.close()
            self.root.destroy()
            raise RuntimeError(f"Unable to bind control port {PORT}.") from exc

        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self.server_thread.start()

    def _apply_layout(self) -> None:
        border_px = WIDTH_TO_PIXELS[self.width_name]
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        self.top.place(x=0, y=0, width=sw, height=border_px)
        self.bottom.place(x=0, y=sh - border_px, width=sw, height=border_px)
        self.left.place(x=0, y=border_px, width=border_px, height=sh - (2 * border_px))
        self.right.place(
            x=sw - border_px,
            y=border_px,
            width=border_px,
            height=sh - (2 * border_px),
        )

    def _set_alpha(self, alpha: float) -> None:
        self.current_alpha = min(1.0, max(0.0, alpha))
        self.root.attributes("-alpha", self.current_alpha)

    def _fade_in(self) -> None:
        step = max(self.target_alpha / FADE_STEPS, 0.01)

        def tick() -> None:
            next_alpha = self.current_alpha + step
            if next_alpha >= self.target_alpha:
                self._set_alpha(self.target_alpha)
                return
            self._set_alpha(next_alpha)
            self.root.after(FADE_STEP_MS, tick)

        tick()

    def _fade_out_then_destroy(self) -> None:
        step = max(self.target_alpha / FADE_STEPS, 0.01)

        def tick() -> None:
            next_alpha = self.current_alpha - step
            if next_alpha <= 0.0:
                self._set_alpha(0.0)
                self.running = False
                self.root.destroy()
                return
            self._set_alpha(next_alpha)
            self.root.after(FADE_STEP_MS, tick)

        tick()

    def _update(self, width_name: str, brightness: int) -> None:
        self.width_name = width_name
        self.brightness = brightness
        self.target_alpha = brightness_to_alpha(brightness)
        self._apply_layout()
        self._set_alpha(self.target_alpha)

    def _start_shutdown(self) -> None:
        if not self.running:
            return
        self._fade_out_then_destroy()

    def _handle_message(self, message: Dict[str, object]) -> Dict[str, object]:
        command = message.get("command")

        if command == "ping":
            return {"ok": True}

        if command == "off":
            self.root.after(0, self._start_shutdown)
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
                self.root.after(0, lambda: self._update(width_name, brightness))
                return {"ok": True}
            return {"ok": False, "error": "invalid payload"}

        return {"ok": False, "error": "unknown command"}

    def _server_loop(self) -> None:
        while self.running:
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
        try:
            self.root.mainloop()
        finally:
            self.running = False
            try:
                self.sock.close()
            except OSError:
                pass


def run_service(width_name: str, brightness: int) -> None:
    service = OverlayService(width_name=width_name, brightness=brightness)
    service.run()
