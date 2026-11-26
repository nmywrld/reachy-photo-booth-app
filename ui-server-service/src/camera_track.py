# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import time
from collections.abc import Callable

import cv2
import numpy as np
from aiortc import VideoStreamTrack
from av import VideoFrame
from workmesh.messages import Frame


def square_crop(image: np.ndarray, size: int) -> np.ndarray:
    """Centre square crop, resized: the same framing the mirror stylizes."""
    h, w = image.shape[:2]
    s = min(h, w)
    y, x = (h - s) // 2, (w - s) // 2
    return cv2.resize(image[y : y + s, x : x + s], (size, size))


class FrameSource:
    """Picks the frame to show: the stylized mirror feed, or the raw camera
    (cropped to the same square) when the mirror has stopped sending."""

    def __init__(
        self,
        size: int = 512,
        fallback_after: float = 1.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.size = size
        self.fallback_after = fallback_after
        self._clock = clock
        self._stylized: Frame | None = None
        self._stylized_at = float("-inf")
        self._raw: Frame | None = None
        self._decoded_from: Frame | None = None
        self._decoded: np.ndarray = np.zeros((size, size, 3), dtype=np.uint8)

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
        frame = self._stylized if self.mirror_live else self._raw
        if frame is None or frame is self._decoded_from:
            return self._decoded  # decode each frame once, not at every recv()
        image = cv2.imdecode(
            np.frombuffer(frame.data, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if image is not None:
            # One fixed output size: switching between mirror and raw never
            # changes the WebRTC resolution.
            if image.shape[0] != self.size or image.shape[1] != self.size:
                image = square_crop(image, self.size)
            self._decoded = image
        self._decoded_from = frame
        return self._decoded


class StreamTrack(VideoStreamTrack):
    """A video track that streams the magic mirror (or the raw camera)."""

    def __init__(self, size: int = 512):
        super().__init__()
        self.source = FrameSource(size)

    def update_frame(self, frame: Frame, stylized: bool = False):
        self.source.update(frame, stylized)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame = VideoFrame.from_ndarray(self.source.current(), format="bgr24")  # type: ignore
        frame.pts = pts
        frame.time_base = time_base
        return frame
