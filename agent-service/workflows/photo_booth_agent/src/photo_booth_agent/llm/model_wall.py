# SPDX-License-Identifier: Apache-2.0
"""Best-effort LLM activity reports for the model wall.

Reports are UDP datagrams sent off the event loop, so the wall being down or
slow can never delay or fail an LLM call. Disabled unless MODEL_WALL_UDP is set.
"""

import asyncio
import contextlib
import json
import os
import socket
from typing import Any


def _send(target: str, payload: bytes) -> None:
    try:
        host, port = target.rsplit(":", 1)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (host, int(port)))
    except (OSError, ValueError):
        pass


def _report(**message: Any) -> None:
    target = os.environ.get("MODEL_WALL_UDP")
    if not target:
        return
    payload = json.dumps(message).encode()
    asyncio.get_running_loop().run_in_executor(None, _send, target, payload)


def report_start(call_id: str) -> None:
    with contextlib.suppress(Exception):
        _report(e="start", id=call_id)


def report_end(call_id: str, raw_response: Any, seconds: float) -> None:
    with contextlib.suppress(Exception):
        usage = raw_response.get("usage") if raw_response is not None else None
        tokens = getattr(usage, "completion_tokens", None)
        _report(e="end", id=call_id, tokens=tokens, seconds=seconds)
