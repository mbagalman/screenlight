from __future__ import annotations

import sys
from typing import Callable, Optional

from ..config import WIDTH_TO_PIXELS, brightness_to_alpha
from .base import OverlayBackend

FADE_STEPS = 8
FADE_STEP_SECONDS = 0.02

# PyObjC is imported at module level but guarded so this module stays
# importable on non-macOS hosts (CI workers, dev machines without PyObjC).
# Methods on MacOSOverlayBackend assume the imports succeeded; the class
# constructor enforces that via get_macos_support_error().
_HAS_PYOBJC = False
if sys.platform == "darwin":
    try:
        from AppKit import (
            NSApplication,
            NSApplicationActivationPolicyAccessory,
            NSBackingStoreBuffered,
            NSColor,
            NSScreen,
            NSView,
            NSWindow,
            NSWindowCollectionBehaviorCanJoinAllSpaces,
            NSWindowCollectionBehaviorFullScreenAuxiliary,
            NSWindowStyleMaskBorderless,
        )
        from PyObjCTools import AppHelper
        from Quartz import (
            CGPathAddRect,
            CGPathCreateMutable,
            CGRectGetHeight,
            CGRectGetWidth,
            CGRectInset,
            CGRectMake,
            CGWindowLevelForKey,
            kCGScreenSaverWindowLevelKey,
        )
        from QuartzCore import CAShapeLayer

        _HAS_PYOBJC = True
    except ImportError:
        pass


def get_macos_support_error() -> Optional[str]:
    if sys.platform != "darwin":
        return "screenlight: macOS backend is only available on macOS."
    if not _HAS_PYOBJC:
        return (
            "screenlight: macOS support requires PyObjC. "
            "Install with `python -m pip install 'pyobjc>=10.0'` and re-run."
        )
    return None


class MacOSOverlayBackend(OverlayBackend):
    def __init__(
        self,
        width_name: str,
        brightness: int,
        on_shutdown: Callable[[], None],
    ) -> None:
        support_error = get_macos_support_error()
        if support_error:
            raise RuntimeError(support_error)

        self.on_shutdown = on_shutdown
        self.width_name = width_name
        self.brightness = brightness
        self.current_alpha = 0.0
        self.target_alpha = brightness_to_alpha(brightness)
        self.closing = False

        self._configure_window()

    def _configure_window(self) -> None:
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

        screen = NSScreen.mainScreen()
        if screen is None:
            raise RuntimeError("screenlight: unable to resolve primary display on macOS.")

        frame = screen.frame()
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame,
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False,
        )

        window.setReleasedWhenClosed_(False)
        window.setOpaque_(False)
        window.setBackgroundColor_(NSColor.clearColor())
        window.setHasShadow_(False)
        window.setIgnoresMouseEvents_(False)
        window.setLevel_(CGWindowLevelForKey(kCGScreenSaverWindowLevelKey))
        window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorFullScreenAuxiliary
        )

        content_view = NSView.alloc().initWithFrame_(frame)
        content_view.setWantsLayer_(True)

        border_layer = CAShapeLayer.layer()
        border_layer.setFillRule_("even-odd")
        content_view.layer().addSublayer_(border_layer)

        window.setContentView_(content_view)
        window.makeKeyAndOrderFront_(None)

        self.window = window
        self.content_view = content_view
        self.border_layer = border_layer

        self._apply_layout()
        self._set_alpha(0.0)
        AppHelper.callLater(0.0, self._fade_to, self.target_alpha)

    def _build_border_path(self):
        bounds = self.content_view.bounds()
        width = WIDTH_TO_PIXELS[self.width_name]

        outer = CGRectMake(0.0, 0.0, CGRectGetWidth(bounds), CGRectGetHeight(bounds))
        inner = CGRectInset(outer, float(width), float(width))

        path = CGPathCreateMutable()
        CGPathAddRect(path, None, outer)
        CGPathAddRect(path, None, inner)
        return path

    def _apply_layout(self) -> None:
        self.border_layer.setFrame_(self.content_view.bounds())
        self.border_layer.setPath_(self._build_border_path())

    def _set_alpha(self, alpha: float) -> None:
        self.current_alpha = min(1.0, max(0.0, alpha))
        color = NSColor.whiteColor().colorWithAlphaComponent_(self.current_alpha)
        self.border_layer.setFillColor_(color.CGColor())

    def _fade_to(self, target: float, on_complete: Optional[Callable[[], None]] = None) -> None:
        start = self.current_alpha
        delta = target - start

        if abs(delta) < 0.001:
            self._set_alpha(target)
            if on_complete:
                on_complete()
            return

        step_amount = delta / FADE_STEPS

        def tick(step_index: int) -> None:
            next_alpha = start + (step_amount * step_index)
            self._set_alpha(next_alpha)

            if step_index >= FADE_STEPS:
                self._set_alpha(target)
                if on_complete:
                    on_complete()
                return

            AppHelper.callLater(FADE_STEP_SECONDS, tick, step_index + 1)

        tick(1)

    def _update_main(self, width_name: str, brightness: int) -> None:
        if self.closing:
            return
        self.width_name = width_name
        self.brightness = brightness
        self.target_alpha = brightness_to_alpha(brightness)
        self._apply_layout()
        self._set_alpha(self.target_alpha)

    def _finish_shutdown(self) -> None:
        self.window.orderOut_(None)
        self.window.close()
        AppHelper.stopEventLoop()

    def _shutdown_main(self) -> None:
        if self.closing:
            return
        self.closing = True
        self._fade_to(0.0, on_complete=self._finish_shutdown)

    def run(self) -> None:
        try:
            AppHelper.runEventLoop()
        finally:
            self.on_shutdown()

    def update(self, width_name: str, brightness: int) -> None:
        AppHelper.callAfter(self._update_main, width_name, brightness)

    def shutdown(self) -> None:
        AppHelper.callAfter(self._shutdown_main)
