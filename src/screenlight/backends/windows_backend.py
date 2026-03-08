from __future__ import annotations

import tkinter as tk
from typing import Callable

from ..config import WIDTH_TO_PIXELS, brightness_to_alpha
from .base import OverlayBackend

TRANSPARENT_KEY = "#00FF00"
FADE_STEPS = 8
FADE_STEP_MS = 20


class WindowsOverlayBackend(OverlayBackend):
    def __init__(
        self,
        width_name: str,
        brightness: int,
        on_shutdown: Callable[[], None],
    ) -> None:
        self.width_name = width_name
        self.brightness = brightness
        self.current_alpha = 0.0
        self.target_alpha = brightness_to_alpha(brightness)
        self.on_shutdown = on_shutdown
        self.closing = False

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
        self.root.bind("<Escape>", lambda _event: self.shutdown())
        self.root.after(0, self._fade_in)

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
                self.root.destroy()
                self.on_shutdown()
                return
            self._set_alpha(next_alpha)
            self.root.after(FADE_STEP_MS, tick)

        tick()

    def _apply_update(self, width_name: str, brightness: int) -> None:
        if self.closing:
            return
        self.width_name = width_name
        self.brightness = brightness
        self.target_alpha = brightness_to_alpha(brightness)
        self._apply_layout()
        self._set_alpha(self.target_alpha)

    def run(self) -> None:
        try:
            self.root.mainloop()
        finally:
            self.on_shutdown()

    def update(self, width_name: str, brightness: int) -> None:
        self.root.after(0, lambda: self._apply_update(width_name, brightness))

    def shutdown(self) -> None:
        if self.closing:
            return
        self.closing = True
        self.root.after(0, self._fade_out_then_destroy)
