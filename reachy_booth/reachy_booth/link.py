"""Connection to the robot's daemon, kept alive in the background.

The testbench connects once at startup and, if the daemon is busy or just
restarted, stays "daemon off" until someone calls ``/api/reconnect``. This app
runs unattended behind the booth, so the link retries by itself: the web server
is always up (``/health`` reports the state), and the camera and motion loops
use whichever robot connection is current.
"""

from __future__ import annotations

import contextlib
import logging
import threading
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("reachy_booth.link")


def connect_localhost(timeout: float = 3.0) -> Any:
    """Connect like the testbench: the daemon on this robot, default media."""
    from reachy_mini import ReachyMini

    return ReachyMini(
        media_backend="default",
        connection_mode="localhost_only",
        timeout=timeout,
    )


class RobotLink:
    """Owns the ``ReachyMini`` connection: connect, watch, reconnect."""

    def __init__(
        self,
        stop_event: threading.Event,
        connect: Callable[[], Any] = connect_localhost,
        retry_delay: float = 3.0,
        dead_after: float = 5.0,
    ) -> None:
        self._stop = stop_event
        self._connect = connect
        self._retry_delay = retry_delay
        self._dead_after = dead_after

        self._lock = threading.Lock()
        self._robot: Any = None
        self._error: str | None = "not connected yet"
        self._connected_at: float | None = None
        self._attempts = 0
        self._wake = threading.Event()
        self._thread = threading.Thread(
            target=self._loop, name="booth-link", daemon=True
        )

    def start(self) -> None:
        self._thread.start()

    def join(self, timeout: float | None = None) -> None:
        self._wake.set()
        self._thread.join(timeout)

    def get(self) -> Any:
        """The connected robot, or None while the daemon is unreachable."""
        with self._lock:
            return self._robot

    def reconnect(self) -> None:
        """Drop the current connection and retry now."""
        self._drop("reconnect requested")
        self._wake.set()

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "connected": self._robot is not None,
                "error": self._error,
                "attempts": self._attempts,
                "connected_for_s": (
                    None
                    if self._connected_at is None
                    else round(time.monotonic() - self._connected_at, 1)
                ),
            }

    # ----------------------------------------------------------------

    def _drop(self, reason: str) -> None:
        with self._lock:
            robot, self._robot = self._robot, None
            self._error = reason
            self._connected_at = None
        if robot is not None:
            with contextlib.suppress(Exception):
                robot.client.disconnect()

    def _alive(self, robot: Any) -> bool:
        client = getattr(robot, "client", None)
        return bool(getattr(client, "_is_alive", True))

    def _loop(self) -> None:
        down_since: float | None = None
        while not self._stop.is_set():
            robot = self.get()
            if robot is None:
                self._attempts += 1
                try:
                    robot = self._connect()
                except Exception as error:
                    with self._lock:
                        self._error = f"{type(error).__name__}: {error}"
                    if self._attempts in (1, 2) or self._attempts % 10 == 0:
                        logger.warning(
                            f"Daemon not reachable (attempt {self._attempts}): {error}"
                        )
                else:
                    with self._lock:
                        self._robot = robot
                        self._error = None
                        self._connected_at = time.monotonic()
                    down_since = None
                    logger.info("Connected to the Reachy Mini daemon")
            elif self._alive(robot):
                down_since = None
            else:
                down_since = down_since or time.monotonic()
                if time.monotonic() - down_since >= self._dead_after:
                    logger.warning("Daemon connection lost; reconnecting")
                    self._drop("connection to the daemon lost")
                    down_since = None
                    continue
            self._wake.wait(1.0 if robot is not None else self._retry_delay)
            self._wake.clear()


class FixedLink:
    """A link around an already-connected robot (tests, simulations)."""

    def __init__(self, robot: Any) -> None:
        self._robot = robot

    def get(self) -> Any:
        return self._robot

    def status(self) -> dict[str, Any]:
        return {"connected": True, "error": None, "attempts": 0, "connected_for_s": 0}

    def reconnect(self) -> None:
        pass
