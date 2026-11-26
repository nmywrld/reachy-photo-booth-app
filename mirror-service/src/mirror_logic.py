# SPDX-License-Identifier: Apache-2.0
"""GPU-free parts of the magic mirror: which style to show, and newest-frame-wins."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable

MAX_STYLE_CHARS = 200


def clean_style(style: str) -> str:
    """One line, bounded length: the style comes from the LLM or a person."""
    return " ".join(style.split())[:MAX_STYLE_CHARS]


def sd_prompt(style: str) -> str:
    """SD-Turbo prompt for a style. Turbo ignores negative prompts (no CFG)."""
    return f"{style}, portrait of a person, high quality, detailed"


class StyleState:
    """The style the mirror shows right now.

    A style someone asked for (by voice) wins until they walk away or it times
    out; otherwise the mirror rotates through idle styles to attract people.
    """

    def __init__(
        self,
        idle_styles: list[str],
        idle_rotate_seconds: float,
        user_style_hold_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not idle_styles:
            raise ValueError("idle_styles must not be empty")
        self._idle = [clean_style(s) for s in idle_styles]
        self._rotate = idle_rotate_seconds
        self._hold = user_style_hold_seconds
        self._clock = clock
        self._user_style: str | None = None
        self._user_set_at = 0.0

    def set_user_style(self, style: str) -> None:
        style = clean_style(style)
        if not style:
            self.reset()
            return
        self._user_style = style
        self._user_set_at = self._clock()

    def reset(self) -> None:
        self._user_style = None

    @property
    def user_chosen(self) -> bool:
        if self._user_style is None:
            return False
        if self._clock() - self._user_set_at > self._hold:
            self._user_style = None
            return False
        return True

    def current(self) -> str:
        if self.user_chosen:
            assert self._user_style is not None
            return self._user_style
        index = int(self._clock() // self._rotate) % len(self._idle)
        return self._idle[index]


class LatestSlot[T]:
    """Holds only the newest item: a slow consumer skips stale frames, never queues."""

    def __init__(self) -> None:
        self._item: T | None = None
        self._ready = asyncio.Event()
        self.dropped = 0

    def put(self, item: T) -> None:
        if self._item is not None:
            self.dropped += 1
        self._item = item
        self._ready.set()

    async def get(self) -> T:
        await self._ready.wait()
        self._ready.clear()
        item = self._item
        self._item = None
        assert item is not None
        return item


class RenderPause:
    """Pause the mirror while hi-res Flux renders run: they share the GPU, and a
    render takes ~40 s with the mirror paused vs ~80 s with it running.

    Each render is tracked by its id with a deadline, so queued photos keep the
    mirror paused until the last one ends, and a lost "ended" message cannot
    pause the mirror forever.
    """

    def __init__(
        self, timeout_seconds: float, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self._timeout = timeout_seconds
        self._clock = clock
        self._pending: dict[str, float] = {}

    def started(self, render_id: str) -> None:
        self._pending[render_id] = self._clock() + self._timeout

    def ended(self, render_id: str) -> None:
        self._pending.pop(render_id, None)

    @property
    def active(self) -> bool:
        now = self._clock()
        for render_id in [
            r for r, deadline in self._pending.items() if deadline <= now
        ]:
            del self._pending[render_id]
        return bool(self._pending)
