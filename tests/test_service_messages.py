from __future__ import annotations

import unittest

from screenlight.service import handle_control_message


class _FakeBackend:
    def __init__(self) -> None:
        self.updated_to: tuple[str, int] | None = None
        self.shutdown_called = False

    def run(self) -> None:  # pragma: no cover - not used in these tests
        return None

    def update(self, width_name: str, brightness: int) -> None:
        self.updated_to = (width_name, brightness)

    def shutdown(self) -> None:
        self.shutdown_called = True


class ServiceMessageTests(unittest.TestCase):
    def test_ping_returns_ok_without_side_effects(self) -> None:
        backend = _FakeBackend()
        response = handle_control_message({"command": "ping"}, backend)

        self.assertEqual(response, {"ok": True})
        self.assertIsNone(backend.updated_to)
        self.assertFalse(backend.shutdown_called)

    def test_update_with_valid_payload_calls_backend_update(self) -> None:
        backend = _FakeBackend()
        response = handle_control_message(
            {"command": "update", "width": "small", "brightness": 6},
            backend,
        )

        self.assertEqual(response, {"ok": True})
        self.assertEqual(backend.updated_to, ("small", 6))

    def test_update_rejects_invalid_payload(self) -> None:
        backend = _FakeBackend()
        response = handle_control_message(
            {"command": "update", "width": "small", "brightness": 11},
            backend,
        )

        self.assertEqual(response, {"ok": False, "error": "invalid payload"})
        self.assertIsNone(backend.updated_to)

    def test_off_calls_backend_shutdown(self) -> None:
        backend = _FakeBackend()
        response = handle_control_message({"command": "off"}, backend)

        self.assertEqual(response, {"ok": True})
        self.assertTrue(backend.shutdown_called)

    def test_unknown_command_returns_error(self) -> None:
        backend = _FakeBackend()
        response = handle_control_message({"command": "boom"}, backend)

        self.assertEqual(response, {"ok": False, "error": "unknown command"})


if __name__ == "__main__":
    unittest.main()
