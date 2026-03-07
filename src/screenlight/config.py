from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

DEFAULT_CONFIG: Dict[str, object] = {
    "width": "medium",
    "brightness": 7,
}

WIDTH_TO_PIXELS = {
    "small": 24,
    "medium": 48,
    "large": 72,
}


def _base_config_dir() -> Path:
    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata)
        return Path.home() / "AppData" / "Roaming"
    if os.name == "posix" and "darwin" in os.sys.platform:
        return Path.home() / "Library" / "Application Support"
    return Path.home() / ".config"


def get_config_file() -> Path:
    return _base_config_dir() / "screenlight" / "config.json"


def load_config() -> Dict[str, object]:
    config_path = get_config_file()
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()

    merged = DEFAULT_CONFIG.copy()
    width = data.get("width")
    brightness = data.get("brightness")

    if isinstance(width, str) and width in WIDTH_TO_PIXELS:
        merged["width"] = width

    if isinstance(brightness, int) and 1 <= brightness <= 10:
        merged["brightness"] = brightness

    return merged


def save_config(config: Dict[str, object]) -> None:
    config_path = get_config_file()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def brightness_to_alpha(brightness: int) -> float:
    # Keep low values visible but not harsh, with linear steps.
    return min(1.0, max(0.1, brightness / 10.0))
