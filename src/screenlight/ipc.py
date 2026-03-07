from __future__ import annotations

import json
import socket
from typing import Any, Dict, Optional

HOST = "127.0.0.1"
PORT = 45871


def send_message(message: Dict[str, Any], timeout: float = 0.75) -> Optional[Dict[str, Any]]:
    data = (json.dumps(message) + "\n").encode("utf-8")

    try:
        with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
            sock.sendall(data)
            sock.shutdown(socket.SHUT_WR)

            chunks = []
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
    except OSError:
        return None

    if not chunks:
        return None

    try:
        return json.loads(b"".join(chunks).decode("utf-8"))
    except json.JSONDecodeError:
        return None
