# SPDX-License-Identifier: Apache-2.0
"""Tracks which models are working, and the LLM's token throughput."""

import json
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

MAX_DATAGRAM_BYTES = 512
LLM_CALL_TTL_SECONDS = 60.0
TOKEN_WINDOW_SECONDS = 60.0


@dataclass(frozen=True)
class Model:
    id: str
    name: str
    role: str
    container: str


# One block per GPU container: NVML reports memory per process, so models that
# share the Riva process cannot be given separate memory figures.
MODELS = (
    Model("llm", "GPT-OSS 20B", "Conversation", "llm"),
    Model("flux", "FLUX.1 Kontext", "Image generation", "image-generator"),
    Model("stt", "Parakeet + VAD + Sortformer", "Speech to text", "riva"),
    Model("tts", "Kokoro", "Text to speech", "text-to-speech"),
    Model("mirror", "SD-Turbo + TAESD", "Magic mirror", "mirror"),
    Model("vision", "SSDLite MobileNetV3", "Presence detection", "tracker"),
)


class ActivityTracker:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._work: dict[str, dict[str, float]] = {m.id: {} for m in MODELS}
        self._pulse_until: dict[str, float] = {m.id: 0.0 for m in MODELS}
        self._token_calls: deque[tuple[float, int, float]] = deque()
        self._last_tps: float | None = None
        self._total_tokens = 0

    def start(self, model: str, key: str, ttl: float) -> None:
        """Mark work as running until stop(), or until ttl if stop() never comes."""
        self._work[model][key] = self._clock() + ttl

    def stop(self, model: str, key: str) -> None:
        self._work[model].pop(key, None)

    def pulse(self, model: str, hold: float) -> None:
        self._pulse_until[model] = max(
            self._pulse_until[model], self._clock() + hold
        )

    def is_active(self, model: str) -> bool:
        now = self._clock()
        work = self._work[model]
        for key in [k for k, expires in work.items() if expires <= now]:
            del work[key]
        return bool(work) or self._pulse_until[model] > now

    def record_tokens(self, tokens: int, seconds: float) -> None:
        if tokens <= 0 or seconds <= 0:
            return
        self._token_calls.append((self._clock(), tokens, seconds))
        self._last_tps = tokens / seconds
        self._total_tokens += tokens

    def handle_llm_datagram(self, data: bytes) -> None:
        """Apply a report from the agent. Malformed datagrams are ignored."""
        if len(data) > MAX_DATAGRAM_BYTES:
            return
        try:
            message = json.loads(data)
            event, call_id = message["e"], str(message["id"])
        except (ValueError, KeyError, TypeError):
            return
        if event == "start":
            self.start("llm", call_id, LLM_CALL_TTL_SECONDS)
        elif event == "end":
            self.stop("llm", call_id)
            tokens, seconds = message.get("tokens"), message.get("seconds")
            if (
                type(tokens) is int
                and type(seconds) in (int, float)
            ):
                self.record_tokens(tokens, float(seconds))

    def token_stats(self) -> dict[str, float | int | None]:
        cutoff = self._clock() - TOKEN_WINDOW_SECONDS
        while self._token_calls and self._token_calls[0][0] < cutoff:
            self._token_calls.popleft()
        tokens = sum(call[1] for call in self._token_calls)
        seconds = sum(call[2] for call in self._token_calls)
        return {
            "last_tokens_per_sec": self._last_tps,
            "avg_tokens_per_sec": tokens / seconds if seconds else None,
            "total_tokens": self._total_tokens,
        }
