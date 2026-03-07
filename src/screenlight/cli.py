from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from typing import Dict

from .config import WIDTH_TO_PIXELS, load_config, save_config
from .ipc import send_message
from .service import run_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="screenlight",
        description="Simulate a ring light using a bright screen border.",
    )
    parser.add_argument("-w", "--width", choices=sorted(WIDTH_TO_PIXELS.keys()))
    parser.add_argument("-b", "--brightness", type=int, help="Brightness level from 1 to 10")
    parser.add_argument("--off", action="store_true", help="Turn off the running overlay")

    # Internal flag used when launching the background service process.
    parser.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def _validate_brightness(brightness: int | None) -> None:
    if brightness is None:
        return
    if not (1 <= brightness <= 10):
        raise SystemExit("error: --brightness must be between 1 and 10")


def _spawn_background_service(config: Dict[str, object]) -> None:
    cmd = [
        sys.executable,
        "-m",
        "screenlight.cli",
        "--serve",
        "--width",
        str(config["width"]),
        "--brightness",
        str(config["brightness"]),
    ]

    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }

    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    else:
        kwargs["start_new_session"] = True

    subprocess.Popen(cmd, **kwargs)


def _wait_for_service(timeout_seconds: float = 2.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = send_message({"command": "ping"}, timeout=0.2)
        if response and response.get("ok"):
            return True
        time.sleep(0.05)
    return False


def _send_update(config: Dict[str, object]) -> bool:
    response = send_message(
        {
            "command": "update",
            "width": config["width"],
            "brightness": int(config["brightness"]),
        }
    )
    return bool(response and response.get("ok"))


def main() -> None:
    args = parse_args()

    if args.serve:
        width = args.width or "medium"
        brightness = args.brightness or 7
        _validate_brightness(brightness)
        run_service(width_name=width, brightness=brightness)
        return

    _validate_brightness(args.brightness)

    if args.off:
        response = send_message({"command": "off"})
        if response and response.get("ok"):
            print("Screenlight turned off.")
            return
        print("No running Screenlight instance found.")
        return

    config = load_config()

    if args.width:
        config["width"] = args.width

    if args.brightness is not None:
        config["brightness"] = args.brightness

    save_config(config)

    if _send_update(config):
        print(f"Screenlight updated: width={config['width']}, brightness={config['brightness']}")
        return

    _spawn_background_service(config)

    # Wait briefly for startup, then push final config to ensure runtime state matches saved config.
    if _wait_for_service():
        _send_update(config)
        print(f"Screenlight started: width={config['width']}, brightness={config['brightness']}")
        return

    raise SystemExit("error: unable to start Screenlight background service")


if __name__ == "__main__":
    main()
