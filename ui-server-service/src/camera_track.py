# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import time
from collections.abc import Callable

import cv2
import numpy as np
from aiortc import VideoStreamTrack
from av import VideoFrame
from workmesh.messages import Frame


def fit_on_blur(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """Whole image centred in width x height, sides filled with a blurred,
    enlarged copy of itself: the square mirror frame on a 16:9 screen."""
    h, w = image.shape[:2]
    # Background: cover the frame, blurred (done small, then upscaled: cheap).
    small_w, small_h = width // 8, height // 8
    scale = max(small_w / w, small_h / h)
    cover = cv2.resize(image, (max(1, round(w * scale)), max(1, round(h * scale))))
    y, x = (cover.shape[0] - small_h) // 2, (cover.shape[1] - small_w) // 2
    background = cv2.GaussianBlur(cover[y : y + small_h, x : x + small_w], (0, 0), 6)
    out = cv2.resize(background, (width, height), interpolation=cv2.INTER_LINEAR)
    out = (out * 0.6).astype(np.uint8)  # dim it so the mirror stands out
    # Foreground: the whole image, as large as fits.
    scale = min(width / w, height / h)
    fw, fh = round(w * scale), round(h * scale)
    y, x = (height - fh) // 2, (width - fw) // 2
    out[y : y + fh, x : x + fw] = cv2.resize(image, (fw, fh))
    return out


class FrameSource:
    """Picks the frame to show: the stylized mirror feed, or the raw camera when
    the mirror has stopped sending. Output is always width x height."""

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fallback_after: float = 1.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.width = width
        self.height = height
        self.fallback_after = fallback_after
        self._clock = clock
        self._stylized: Frame | None = None
        self._stylized_at = float("-inf")
        self._raw: Frame | None = None
        self._decoded_from: Frame | None = None
        self._decoded: np.ndarray = np.zeros((height, width, 3), dtype=np.uint8)

    def update(self, frame: Frame, stylized: bool) -> None:
        if stylized:
            self._stylized = frame
            self._stylized_at = self._clock()
        else:
            self._raw = frame

    @property
    def mirror_live(self) -> bool:
        return self._clock() - self._stylized_at <= self.fallback_after

    def current(self) -> np.ndarray:
        stylized = self.mirror_live
        frame = self._stylized if stylized else self._raw
        if frame is None or frame is self._decoded_from:
            return self._decoded  # build each frame once, not at every recv()
        data = np.frombuffer(frame.data, dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if image is not None:
            if stylized:
                image = fit_on_blur(image, self.width, self.height)
            else:
                # The raw camera, as the original booth showed it.
                image = cv2.resize(image, (self.width, self.height))
            self._decoded = image
        self._decoded_from = frame
        return self._decoded


class StreamTrack(VideoStreamTrack):
    """A video track that streams the magic mirror (or the raw camera)."""

    def __init__(self, width: int, height: int):
        super().__init__()
        self.source = FrameSource(width, height)

    def update_frame(self, frame: Frame, stylized: bool = False):
        self.source.update(frame, stylized)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame = VideoFrame.from_ndarray(self.source.current(), format="bgr24")  # type: ignore
        frame.pts = pts
        frame.time_base = time_base
        return frame
