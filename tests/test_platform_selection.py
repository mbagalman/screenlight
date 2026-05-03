from __future__ import annotations

import unittest

from screenlight.service import UnsupportedPlatformError, select_backend_class


class PlatformSelectionTests(unittest.TestCase):
    def test_windows_platform_selects_windows_backend(self) -> None:
        backend_class = select_backend_class("win32")
        self.assertEqual(backend_class.__name__, "WindowsOverlayBackend")

    def test_macos_platform_returns_backend_or_dependency_error(self) -> None:
        try:
            backend_class = select_backend_class("darwin")
            self.assertEqual(backend_class.__name__, "MacOSOverlayBackend")
        except UnsupportedPlatformError as exc:
            message = str(exc)
            self.assertTrue(
                "macOS support requires PyObjC" in message
                or "only available on macOS" in message,
                f"unexpected error message: {message}",
            )

    def test_unknown_platform_raises_actionable_error(self) -> None:
        with self.assertRaises(UnsupportedPlatformError) as context:
            select_backend_class("linux")
        self.assertIn("unsupported platform", str(context.exception))


if __name__ == "__main__":
    unittest.main()
