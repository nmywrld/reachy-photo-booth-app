# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Wireless Reachy Mini camera, served by the on-robot Reachy Booth app.

The Reachy Booth app (``reachy_booth/`` in this repository) runs on the robot,
reads the camera through the Reachy Mini Python SDK and serves:

* ``GET /camera/stream``: an MJPEG live stream at a reduced size, which this
  module reads on a background thread, keeping only the newest frame;
* ``GET /camera/frame.jpg``: a full-resolution still, fetched for photos.

Plain HTTP over TCP rides out Wi-Fi hiccups as lag; when the stream does drop,
the reader reconnects with backoff and logs the cause once.
"""

import logging
import threading
import time
from urllib.parse import urlencode, urlparse

import cv2
import numpy as np
import numpy.typing as npt
import requests

REACHY_SCHEME = "reachy"
DEFAULT_PORT = 8042  # the Reachy Booth app's port

Frame = npt.NDArray[np.uint8]

SOI = b"\xff\xd8"  # JPEG start / end of image markers
EOI = b"\xff\xd9"


def parse_reachy_url(value: str) -> str | None:
    """Return the app's base URL for ``reachy://host[:port]``, else None."""
    try:
        parsed = urlparse(value)
        port = parsed.port
    except ValueError:
        return None
    if parsed.scheme != REACHY_SCHEME or not parsed.hostname:
        return None
    return f"http://{parsed.hostname}:{port or DEFAULT_PORT}"


def _decode(jpeg: bytes) -> Frame | None:
    return cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)


class ReachyBoothCamera:
    """Latest-frame reader for the Reachy Booth app's camera endpoints."""

    def __init__(
        self,
        base_url: str,
        width: int,
        height: int,
        fps: int,
        quality: int = 65,
        connect_timeout: float = 5.0,
        read_timeout: float = 10.0,
        still_timeout: float = 8.0,
        max_frame_age: float = 2.0,
        max_reconnect_delay: float = 10.0,
        logger: logging.Logger | None = None,
    ) -> None:
        self._log = logger or logging.getLogger(__name__)
        self.base_url = base_url
        self.stream_url = f"{base_url}/camera/stream?" + urlencode(
            {"width": width, "height": height, "fps": fps, "quality": quality}
        )
        self._timeouts = (connect_timeout, read_timeout)
        self._still_timeout = (connect_timeout, still_timeout)
        self._max_frame_age = max_frame_age
        self._max_reconnect_delay = max_reconnect_delay

        self._cond = threading.Condition()
        self._frame: Frame | None = None
        self._seq = 0
        self._frame_at = 0.0
        self._closed = False
        self._response: requests.Response | None = None
        self._session = requests.Session()
        self._session.trust_env = False  # LAN only: ignore host proxies

        self._thread = threading.Thread(
            target=self._run, name="reachy-booth-camera", daemon=True
        )
        self._thread.start()

    # ------------------------------------------------------------ public API

    def read(
        self, timeout: float = 5.0, after: int | None = None
    ) -> tuple[bool, Frame | None]:
        """Wait for a frame newer than ``after`` (default: the last one seen).

        Returns ``(False, None)`` on timeout or once released, so callers can
        retry instead of treating a Wi-Fi hiccup as end of stream.
        """
        with self._cond:
            last = self._seq if after is None else after
            self._cond.wait_for(
                lambda: self._closed or self._seq > last, timeout=timeout
            )
            if self._closed or self._seq <= last or self._frame is None:
                return False, None
            return True, self._frame

    def latest(self) -> tuple[bool, Frame | None]:
        """Newest streamed frame if it is still live (never an old still)."""
        with self._cond:
            fresh = time.monotonic() - self._frame_at <= self._max_frame_age
            if self._frame is None or not fresh:
                return False, None
            return True, self._frame

    def capture_still(self, quality: int = 90) -> tuple[bool, Frame | None]:
        """Full-resolution still from the robot (blocking; call off the loop)."""
        try:
            resp = self._session.get(
                f"{self.base_url}/camera/frame.jpg",
                params={"quality": quality},
                timeout=self._still_timeout,
            )
            resp.raise_for_status()
        except requests.RequestException as error:
            self._log.warning(f"Reachy still capture failed: {error}")
            return False, None
        frame = _decode(resp.content)
        return frame is not None, frame

    def isOpened(self) -> bool:  # noqa: N802 - mirrors cv2.VideoCapture
        return not self._closed

    def release(self) -> None:
        with self._cond:
            if self._closed:
                return
            self._closed = True
            self._cond.notify_all()
        response = self._response
        if response is not None:
            response.close()  # unblocks the reader
        self._thread.join(timeout=5)
        self._session.close()

    # ------------------------------------------------------------ internals

    def _run(self) -> None:
        delay = 1.0
        outage: str | None = None
        while not self._closed:
            try:
                with self._session.get(
                    self.stream_url, stream=True, timeout=self._timeouts
                ) as resp:
                    resp.raise_for_status()
                    self._response = resp
                    first = True
                    for _ in self._frames(resp):
                        if first:  # once per connection
                            self._log.info(
                                f"Reachy video streaming from {self.base_url}"
                            )
                            first, outage, delay = False, None, 1.0
                    reason = "stream ended"
            except (requests.RequestException, OSError, AttributeError) as error:
                # AttributeError: urllib3 after release() closed the response.
                reason = str(error)
            finally:
                self._response = None
            if self._closed:
                break
            if reason != outage:
                self._log.warning(
                    f"Reachy video unavailable from {self.base_url}: {reason}. "
                    "Is the reachy_booth app running on the robot?"
                )
                outage = reason
            with self._cond:
                self._cond.wait_for(lambda: self._closed, timeout=delay)
            delay = min(delay * 2, self._max_reconnect_delay)

    def _frames(self, resp: requests.Response):
        """Yield once per decoded frame; JPEGs are found by their markers."""
        buffer = b""
        for chunk in resp.iter_content(chunk_size=16384):
            if self._closed:
                return
            buffer += chunk
            while True:
                start = buffer.find(SOI)
                if start < 0:
                    buffer = buffer[-1:]  # keep a possible split marker byte
                    break
                end = buffer.find(EOI, start + 2)
                if end < 0:
                    buffer = buffer[start:]
                    break
                jpeg, buffer = buffer[start : end + 2], buffer[end + 2 :]
                frame = _decode(jpeg)
                if frame is None:
                    continue
                with self._cond:
                    self._frame = frame
                    self._frame_at = time.monotonic()
                    self._seq += 1
                    self._cond.notify_all()
                yield
