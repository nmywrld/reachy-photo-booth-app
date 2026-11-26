# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from ipaddress import IPv4Address
from pathlib import Path
from typing import Literal

from pydantic import Field
from workmesh.config import BaseConfig


class Robot(Enum):
    RESEARCHER = "researcher"


DEFAULT_IDLE_STYLES = [
    "oil painting, dramatic lighting",
    "colorful pop art comic book",
    "Japanese anime illustration",
    "watercolor painting, soft pastel colors",
    "3D animated movie character",
    "Van Gogh starry night painting style",
    "pencil sketch, detailed shading",
    "cyberpunk neon portrait",
]


class MirrorConfig(BaseConfig):
    """Configuration for the magic mirror stylizer."""

    robot_id: Robot = Field(default=Robot.RESEARCHER)
    model: str = Field(default="stabilityai/sd-turbo")
    taesd: str = Field(default="madebyollin/taesd")
    backend: Literal["trt", "compile", "eager"] = Field(
        default="trt",
        description="trt falls back to torch.compile if the engine cannot be built.",
    )
    dtype: Literal["bf16", "fp16"] = Field(default="bf16")
    steps: int = Field(default=1, ge=1, le=2, description="Denoising steps per frame")
    strength: float = Field(
        default=0.5,
        gt=0.0,
        lt=1.0,
        description="img2img strength: lower keeps the person, higher the style",
    )
    size: int = Field(default=512, ge=256, le=768, multiple_of=64)
    jpeg_quality: int = Field(default=80, ge=10, le=100)
    max_fps: float = Field(
        default=20.0,
        gt=0,
        description="Cap so the mirror leaves GPU time for Flux renders",
    )
    engine_cache_dir: Path = Field(default=Path("/cache/engines"))
    idle_styles: list[str] = Field(default=DEFAULT_IDLE_STYLES, min_length=1)
    idle_rotate_seconds: float = Field(default=20.0, gt=0)
    user_style_hold_seconds: float = Field(
        default=600.0,
        gt=0,
        description="A requested style reverts to idle styles after this long, "
        "or as soon as the person leaves",
    )
    pause_during_render: bool = Field(
        default=True,
        description="Freeze the mirror on its last frame while a shutter photo's "
        "hi-res Flux render runs (~40 s instead of ~80 s)",
    )
    pause_timeout_seconds: float = Field(
        default=180.0,
        gt=0,
        description="Resume anyway if a render's end is never reported",
    )
    hold_frame_interval: float = Field(
        default=0.5,
        gt=0,
        description="While paused, re-send the last frame this often so the kiosk "
        "keeps showing it instead of falling back to the raw camera",
    )
    http_bind_address: IPv4Address = Field(default=IPv4Address("0.0.0.0"))
    http_bind_port: int = Field(default=7072)
