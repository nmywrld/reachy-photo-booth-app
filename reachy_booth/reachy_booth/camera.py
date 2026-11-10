"""Camera frames for the photo booth.

One grabber thread reads the robot's camera through the SDK
(``reachy_mini.media.get_frame()``; on the robot this is the local backend, no
network involved) and keeps only the newest frame. HTTP handlers encode JPEGs
from it on demand: a reduced live stream and full-resolution stills.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

import cv2
import numpy as np
import numpy.typing as npt

logger = logging.getLogger("reachy_booth.camera")

Frame = npt.NDArray[np.uint8]


def encode_jpeg(
    frame: Frame, width: int | None = None, height: int | None = None, quality: int = 85
) -> bytes:
    """Encode a BGR frame as JPEG, resized to ``width`` x ``height`` if given."""
    if width and height and (frame.shape[1] != width or frame.shape[0] != height):
        frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    ok, buffer = cv2.imencode(
        ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, int(np.clip(quality, 1, 100))]
    )
    if not ok:
        raise RuntimeError("JPEG encoding failed")
    return buffer.tobytes()


class FrameGrabber:
    """Keeps the newest camera frame; readers wait for a newer one."""

    def __init__(
        self, link: Any, stop_event: threading.Event, max_fps: float = 30.0
    ) -> None:
        self._link = link  # .get() -> connected robot, or None
        self._stop = stop_event
        self._period = 1.0 / max_fps
        self._cond = threading.Condition()
        self._frame: Frame | None = None
        self._seq = 0
        self._frame_at = 0.0
        self._fps = 0.0
        self._thread = threading.Thread(
            target=self._loop, name="booth-camera", daemon=True
        )

    def start(self) -> None:
        self._thread.start()

    def join(self, timeout: float | None = None) -> None:
        with self._cond:
            self._cond.notify_all()
        self._thread.join(timeout)

    def latest(self, max_age: float) -> Frame | None:
        """Newest frame if it is at most ``max_age`` seconds old."""
        with self._cond:
            if self._frame is None or time.monotonic() - self._frame_at > max_age:
                return None
            return self._frame

    def wait_newer(self, seq: int, timeout: float) -> tuple[int, Frame | None]:
        """Wait for a frame newer than ``seq``; returns ``(seq, frame)``."""
        with self._cond:
            self._cond.wait_for(
                lambda: self._stop.is_set() or self._seq > seq, timeout=timeout
            )
            if self._seq <= seq:
                return seq, None
            return self._seq, self._frame

    def stats(self) -> dict[str, Any]:
        with self._cond:
            age = time.monotonic() - self._frame_at if self._frame_at else None
            shape = None if self._frame is None else list(self._frame.shape[:2][::-1])
            return {
                "frame_age_s": None if age is None else round(age, 3),
                "fps": round(self._fps, 1),
                "resolution": shape,
            }

    def _loop(self) -> None:
        last_log = 0.0
        while not self._stop.is_set():
            start = time.monotonic()
            robot = self._link.get()
            if robot is None:  # daemon unreachable: wait for the link
                self._stop.wait(0.5)
                continue
            try:
                frame = robot.media.get_frame()
            except Exception as error:
                frame = None
                if start - last_log > 5.0:
                    last_log = start
                    logger.warning(f"Camera read failed: {error}")
            if frame is not None:
                with self._cond:
                    if self._frame_at:
                        dt = start - self._frame_at
                        if dt > 0:
                            self._fps = 0.9 * self._fps + 0.1 / dt
                    self._frame = frame
                    self._frame_at = start
                    self._seq += 1
                    self._cond.notify_all()
                self._stop.wait(max(0.0, self._period - (time.monotonic() - start)))
            else:
                self._stop.wait(0.01)
