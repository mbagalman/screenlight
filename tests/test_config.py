from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from screenlight.config import DEFAULT_CONFIG, load_config, save_config


class ConfigTests(unittest.TestCase):
    def test_load_returns_defaults_when_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "screenlight" / "config.json"
            with mock.patch("screenlight.config.get_config_file", return_value=config_path):
                loaded = load_config()

        self.assertEqual(loaded, DEFAULT_CONFIG)

    def test_load_merges_partial_values_with_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "screenlight" / "config.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text('{"brightness": 9}', encoding="utf-8")

            with mock.patch("screenlight.config.get_config_file", return_value=config_path):
                loaded = load_config()

        self.assertEqual(loaded["width"], DEFAULT_CONFIG["width"])
        self.assertEqual(loaded["brightness"], 9)

    def test_load_ignores_invalid_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "screenlight" / "config.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text('{"width": "huge", "brightness": 88}', encoding="utf-8")

            with mock.patch("screenlight.config.get_config_file", return_value=config_path):
                loaded = load_config()

        self.assertEqual(loaded, DEFAULT_CONFIG)

    def test_save_then_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "screenlight" / "config.json"
            with mock.patch("screenlight.config.get_config_file", return_value=config_path):
                save_config({"width": "large", "brightness": 3})
                loaded = load_config()

        self.assertEqual(loaded, {"width": "large", "brightness": 3})


if __name__ == "__main__":
    unittest.main()
