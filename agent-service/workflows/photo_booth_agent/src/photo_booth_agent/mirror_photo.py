# SPDX-License-Identifier: Apache-2.0
"""Magic mirror shutter pipeline.

On a `mirror_capture` request (sent by the interaction manager at the flash):
  1. grab the instant stylized frame (mirror) and the full-resolution still (camera)
  2. frame the instant photo, upload it, make a download page + QR code, and
     report it at once (`mirror_photo` TOOL_CALL_STARTED) so the kiosk shows it
  3. render the still with FLUX.1 Kontext in the current mirror style; the
     download page picks the hi-res file up by itself (`mirror_photo` COMPLETED)

Progress goes out as ToolStatus(name="mirror_photo"), JSON in `response`.
"""

from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import os
import time
import uuid
from datetime import timedelta

import aiohttp
from minio import Minio
from PIL import Image, ImageFilter
from pydantic import BaseModel, Field
from workmesh.messages import ImageGeneration, ToolStatus
from workmesh.service import Service, subscribe

from photo_booth_agent.configs.minio import POLICY_TEMPLATE, MinioConfig
from photo_booth_agent.constant import SERVICE_NAME
from photo_booth_agent.tools.image_generation import (
    _generate_qr_code,
    _overlay_dell_logo,
    _parse_duration,
    _upload_to_minio,
)
from photo_booth_agent.utils import initialize_minio
from workmesh import mirror_capture_topic, tool_status_topic

logger = logging.getLogger(SERVICE_NAME)

MIRROR_PHOTO_TOOL = "mirror_photo"
IN_DOCKER = os.path.exists("/.dockerenv")


def flux_prompt(style: str) -> str:
    """FLUX.1 Kontext edit instruction for a mirror style (same rules as the agent)."""
    return (
        f"Restyle the entire image to {style}, while keeping the subject(s) in the "
        "exact same position, scale, and pose, and preserving their exact facial "
        "features, hairstyle, gender, body type, age, and ethnicity."
    )


def download_page_html(instant_url: str, hires_url: str | None) -> str:
    """Shows the instant photo, then swaps in the hi-res render once it exists."""
    poll = ""
    if hires_url:
        poll = f"""
<script>
  const hires = {json.dumps(hires_url)};
  const status = document.getElementById("status");
  let tries = 0;
  function check() {{
    const probe = new Image();
    probe.onload = () => {{
      document.getElementById("photo").src = hires;
      document.getElementById("download").href = hires;
      status.textContent = "Hi-res version ready!";
    }};
    probe.onerror = () => {{
      if (++tries < 120) setTimeout(check, 5000);
      else status.textContent = "";
    }};
    probe.src = hires + (hires.includes("?") ? "&" : "?") + "t=" + Date.now();
  }}
  check();
</script>"""
    status = (
        "Painting the hi-res version, this page updates by itself…" if hires_url else ""
    )
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your magic mirror photo</title>
<style>
  body {{ margin: 0; min-height: 100vh; display: flex; flex-direction: column;
         align-items: center; justify-content: center; gap: 16px; padding: 20px;
         box-sizing: border-box; color: #fff; background: #1a1a1a;
         font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
  img {{ max-width: 100%; max-height: 70vh; border-radius: 12px; }}
  a {{ display: block; padding: 14px 28px; border-radius: 12px; background: #007aff;
       color: #fff; text-decoration: none; font-weight: 600; }}
  #status {{ opacity: .8; text-align: center; }}
</style></head>
<body>
  <img id="photo" src="{instant_url}" alt="Your photo">
  <p id="status">{status}</p>
  <a id="download" href="{instant_url}" download>Download</a>
  {poll}
</body></html>"""


def square_to_landscape(jpeg: bytes, ratio: float = 3 / 2) -> bytes:
    """Put the square mirror frame on a blurred 3:2 copy of itself.

    The photo frame's opening is landscape; cropping the square to fit would cut
    off the top of the head, so the whole square is kept and the sides filled.
    """
    square = Image.open(io.BytesIO(jpeg)).convert("RGB")
    h = square.height
    w = int(h * ratio)
    background = square.resize((w, w)).crop((0, (w - h) // 2, w, (w + h) // 2))
    background = background.filter(ImageFilter.GaussianBlur(h // 20))
    background.paste(square, ((w - square.width) // 2, 0))
    out = io.BytesIO()
    background.save(out, "PNG")
    return out.getvalue()


class MirrorPhotoConfig(BaseModel):
    mirror_url: str = Field(
        default="http://mirror:7072" if IN_DOCKER else "http://localhost:7072"
    )
    camera_url: str = Field(
        default="http://camera:7071" if IN_DOCKER else "http://localhost:7071"
    )
    flux_url: str = Field(
        default="http://image-generator:8000/v1/infer"
        if IN_DOCKER
        else "http://localhost:9090/v1/infer"
    )
    flux_steps: int = Field(default=20, ge=1, le=50)
    disable_safety_checker: bool = True
    internal_minio: MinioConfig = Field(default_factory=MinioConfig)
    external_minio: MinioConfig | None = None
    link_expires: str = Field(
        default="00:30:00",
        description="How long the QR download page and photos stay reachable "
        "(HH:MM:SS). Longer than the Flux render, so the hi-res photo arrives.",
    )


def _minio(cfg: MinioConfig) -> Minio:
    return initialize_minio(
        cfg.base_url,
        cfg.access_key,
        cfg.secret_key.get_secret_value(),
        cfg.bucket,
        policy=POLICY_TEMPLATE.format(bucket=cfg.bucket),
        secure=cfg.secure,
        create_bucket=cfg.create_bucket,
        timeout=cfg.timeout,
        num_retries=cfg.num_retries,
        backoff_factor=cfg.backoff_factor,
    )


class MirrorPhotoService(Service):
    """Runs alongside the agent; handles `mirror_capture` requests."""

    def __init__(self, config, photo_config: MirrorPhotoConfig) -> None:
        super().__init__(config)
        self.cfg = photo_config
        self.expires: timedelta = _parse_duration(photo_config.link_expires)
        self._internal: Minio | None = None
        self._external: Minio | None = None
        self._flux_lock = asyncio.Lock()  # one render at a time; later ones queue

    def _clients(self) -> tuple[Minio, Minio | None]:
        if self._internal is None:
            self._internal = _minio(self.cfg.internal_minio)
            if self.cfg.external_minio is not None:
                try:
                    self._external = _minio(self.cfg.external_minio)
                except Exception:
                    logger.exception("External MinIO unavailable: no QR codes")
        return self._internal, self._external

    def _internal_url(self, key: str) -> str:
        c = self.cfg.internal_minio
        return f"http://{c.base_url}/{c.bucket}/{key}"

    async def _report(self, action_uuid: str, status: int, **data: str | None) -> None:
        await self.publish(
            tool_status_topic,
            ToolStatus(
                action_uuid=action_uuid,
                name=MIRROR_PHOTO_TOOL,
                status=status,  # type: ignore[arg-type]
                timestamp=int(time.time() * 1000),
                response=json.dumps(data),
            ),
        )

    async def _get(self, session: aiohttp.ClientSession, url: str) -> bytes:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
            if r.status == 409:
                raise RuntimeError("No one in front of the mirror")
            r.raise_for_status()
            return await r.read()

    async def _upload(
        self, client: Minio, bucket: str, key: str, data: bytes, ctype: str
    ):
        key_or_none = await asyncio.to_thread(
            _upload_to_minio, client, bucket, key, data, ctype
        )
        if key_or_none is None:
            raise RuntimeError(f"Upload of {key} failed")

    @subscribe(mirror_capture_topic)
    async def on_capture(self, request: ImageGeneration) -> None:
        action_uuid = request.action_uuid or str(uuid.uuid4())
        started = False
        try:
            internal, external = await asyncio.to_thread(self._clients)
            async with aiohttp.ClientSession() as session:
                # The instant frame first: it is the one that matches the flash.
                instant_jpeg = await self._get(
                    session, f"{self.cfg.mirror_url}/frame.jpg?fresh=1"
                )
                style_info = json.loads(
                    await self._get(session, f"{self.cfg.mirror_url}/style")
                )
                still = await self._get(session, f"{self.cfg.camera_url}/capture")
            style = style_info.get("style") or "a colorful painting"
            logger.info(f"Mirror photo {action_uuid}: style {style!r}")

            instant_png = await asyncio.to_thread(
                lambda: _overlay_dell_logo(square_to_landscape(instant_jpeg))
            )
            base = f"mirror/{action_uuid}"
            ibucket = self.cfg.internal_minio.bucket
            await self._upload(
                internal, ibucket, f"{base}/instant.png", instant_png, "image/png"
            )

            qrcode_url = None
            hires_link = None
            if external is not None and self.cfg.external_minio is not None:
                qrcode_url, hires_link = await self._share(
                    internal, external, base, instant_png
                )
            await self._report(
                action_uuid,
                ToolStatus.Status.TOOL_CALL_STARTED,
                image_url=self._internal_url(f"{base}/instant.png"),
                qrcode_url=qrcode_url,
                style=style,
            )
            started = True

            async with self._flux_lock:
                hires_png = await self._render(still, style)
            await self._upload(
                internal, ibucket, f"{base}/hires.png", hires_png, "image/png"
            )
            # Report as soon as the kiosk has it: this also resumes the mirror,
            # which is paused while Flux renders. The slower upload for the
            # download page (which polls for it) happens afterwards.
            await self._report(
                action_uuid,
                ToolStatus.Status.TOOL_CALL_COMPLETED,
                image_url=self._internal_url(f"{base}/hires.png"),
                qrcode_url=qrcode_url,
                style=style,
            )
            if external is not None and hires_link is not None:
                assert self.cfg.external_minio is not None
                try:
                    await self._upload(
                        external,
                        self.cfg.external_minio.bucket,
                        f"{base}/hires.png",
                        hires_png,
                        "image/png",
                    )
                except Exception as exc:
                    # The kiosk has the hi-res photo; only the download page
                    # keeps showing the instant one.
                    logger.warning(f"Mirror photo {action_uuid}: share failed: {exc!r}")
            logger.info(f"Mirror photo {action_uuid}: hi-res done")
        except Exception as exc:
            logger.exception(f"Mirror photo {action_uuid} failed: {exc!r}")
            await self._report(
                action_uuid,
                ToolStatus.Status.TOOL_CALL_FAILED,
                error=str(exc),
                stage="render" if started else "capture",
            )

    async def _share(
        self, internal: Minio, external: Minio, base: str, instant_png: bytes
    ) -> tuple[str | None, str | None]:
        """Upload for download; returns (internal QR image URL, hi-res link)."""
        assert self.cfg.external_minio is not None
        bucket = self.cfg.external_minio.bucket
        try:
            await self._upload(
                external, bucket, f"{base}/instant.png", instant_png, "image/png"
            )
            instant_link = await asyncio.to_thread(
                external.presigned_get_object,
                bucket,
                f"{base}/instant.png",
                expires=self.expires,
            )
            # Signed now, uploaded when Flux finishes; the page polls for it.
            hires_link = await asyncio.to_thread(
                external.presigned_get_object,
                bucket,
                f"{base}/hires.png",
                expires=self.expires,
            )
            page = download_page_html(instant_link, hires_link).encode()
            await self._upload(
                external, bucket, f"{base}/index.html", page, "text/html"
            )
            page_link = await asyncio.to_thread(
                external.presigned_get_object,
                bucket,
                f"{base}/index.html",
                expires=self.expires,
                response_headers={
                    "response-content-type": "text/html",
                    "response-content-disposition": "inline",
                },
            )
            qr_key = f"qrcode/mirror_{uuid.uuid4()}.png"
            await self._upload(
                internal,
                self.cfg.internal_minio.bucket,
                qr_key,
                _generate_qr_code(page_link),
                "image/png",
            )
            return self._internal_url(qr_key), hires_link
        except Exception:
            logger.exception("Sharing the mirror photo failed; no QR code")
            return None, None

    async def _render(self, still: bytes, style: str) -> bytes:
        request = {
            "prompt": flux_prompt(style),
            "aspect_ratio": "3:2",
            "resize_response_image": False,
            "image": f"data:image/png;base64,{base64.b64encode(still).decode()}",
            "steps": self.cfg.flux_steps,
            "disable_safety_checker": self.cfg.disable_safety_checker,
        }
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                self.cfg.flux_url,
                json=request,
                timeout=aiohttp.ClientTimeout(total=300),
            ) as response,
        ):
            response.raise_for_status()
            result = await response.json()
        image = base64.b64decode(result["artifacts"][0]["base64"])
        return await asyncio.to_thread(_overlay_dell_logo, image)
