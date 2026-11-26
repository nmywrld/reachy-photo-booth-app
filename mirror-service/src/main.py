# SPDX-License-Identifier: Apache-2.0
"""Magic mirror: stylizes the live camera feed with SD-Turbo in near real time.

In:  camera_frame (newest frame wins), mirror_style (ImageGeneration.prompt),
     user_state (a style someone asked for ends when they leave),
     tool_status (mirror_photo renders: pause while Flux renders)
Out: stylized_frame (JPEG Frame, same index/timestamp as the source frame;
     while paused, the last frame is re-sent so the kiosk holds it)
HTTP (port 7072): GET /frame.jpg, GET /style, GET /health
"""

import asyncio
import time

from aiohttp import web
from configuration import MirrorConfig
from mirror_logic import LatestSlot, RenderPause, StyleState, sd_prompt
from workmesh.config import load_config
from workmesh.messages import (
    Frame,
    ImageEncoding,
    ImageGeneration,
    PresenceStatus,
    Robot,
    ToolStatus,
    UserState,
)
from workmesh.service import Service, subscribe
from workmesh.service_executor import ServiceExecutor

from workmesh import (
    camera_frame_topic,
    mirror_style_topic,
    stylized_frame_topic,
    tool_status_topic,
    user_state_topic,
)

MIRROR_PHOTO_TOOL = "mirror_photo"


class MirrorService(Service):
    def __init__(self, config: MirrorConfig) -> None:
        super().__init__(config)
        self._config = config
        self._me = getattr(Robot, config.robot_id.name)
        self._frames: LatestSlot[Frame] = LatestSlot()
        self._styles = StyleState(
            config.idle_styles,
            config.idle_rotate_seconds,
            config.user_style_hold_seconds,
        )
        self._stylizer = None
        self._active_style: str | None = None
        self._latest_jpeg: bytes | None = None
        self._latest_frame: Frame | None = None
        self._latest_at = float("-inf")  # monotonic time of the last new frame
        self._force_until = float("-inf")  # stylize even while paused until then
        self._frames_out = 0
        self._pause = RenderPause(config.pause_timeout_seconds)
        self._was_paused = False
        self.create_task(self._run_mirror())
        self.create_task(self._hold_while_paused())

    @subscribe(camera_frame_topic)
    async def on_camera_frame(self, frame: Frame) -> None:
        if frame.robot_id == self._me:
            self._frames.put(frame)

    @subscribe(mirror_style_topic)
    async def on_style(self, message: ImageGeneration) -> None:
        self.logger.info(f"Style requested: {message.prompt!r}")
        self._styles.set_user_style(message.prompt)

    @subscribe(user_state_topic)
    async def on_user_state(self, message: UserState) -> None:
        if (
            message.robot_id == self._me
            and message.status == PresenceStatus.USER_DISAPPEARED
        ):
            self._styles.reset()

    @subscribe(tool_status_topic)
    async def on_tool_status(self, message: ToolStatus) -> None:
        # The shutter pipeline reports STARTED once the instant photo is out and
        # the Flux render begins, then COMPLETED or FAILED when it ends.
        if message.name != MIRROR_PHOTO_TOOL or not self._config.pause_during_render:
            return
        if message.status == ToolStatus.TOOL_CALL_STARTED:
            self._pause.started(message.action_uuid)
        elif message.status in (
            ToolStatus.TOOL_CALL_COMPLETED,
            ToolStatus.TOOL_CALL_FAILED,
        ):
            self._pause.ended(message.action_uuid)

    def _paused(self) -> bool:
        paused = self._pause.active
        if paused != self._was_paused:
            self.logger.info(
                "Mirror paused for a hi-res render" if paused else "Mirror resumed"
            )
            self._was_paused = paused
        return paused

    async def _hold_while_paused(self) -> None:
        """Re-send the last stylized frame: no GPU work, the screen stays still."""
        while True:
            await asyncio.sleep(self._config.hold_frame_interval)
            if self._paused() and self._latest_frame is not None:
                await self.publish(stylized_frame_topic, self._latest_frame)

    async def _run_mirror(self) -> None:
        from stylizer import Stylizer  # heavy import: torch/diffusers

        c = self._config
        self.logger.info(f"Loading stylizer ({c.model}, backend={c.backend})...")
        self._stylizer = await asyncio.to_thread(
            Stylizer,
            c.model,
            c.taesd,
            c.backend,
            c.dtype,
            c.steps,
            c.strength,
            c.size,
            c.jpeg_quality,
            c.engine_cache_dir,
        )
        min_interval = 1.0 / c.max_fps
        last = 0.0
        stats_at = time.monotonic()
        while True:
            frame = await self._frames.get()
            if self._paused() and time.monotonic() > self._force_until:
                continue  # Flux has the GPU; drop camera frames until it is done
            wait = min_interval - (time.monotonic() - last)
            if wait > 0:
                await asyncio.sleep(wait)
            last = time.monotonic()
            style = self._styles.current()
            try:
                if style != self._active_style:
                    self.logger.info(f"Mirror style -> {style!r}")
                    await asyncio.to_thread(self._stylizer.set_style, sd_prompt(style))
                    self._active_style = style
                jpeg = await asyncio.to_thread(self._stylizer.stylize_jpeg, frame.data)
            except Exception:
                self.logger.exception(f"Failed to stylize frame {frame.index}")
                continue
            self._latest_jpeg = jpeg
            self._latest_at = time.monotonic()
            self._frames_out += 1
            self._latest_frame = Frame(
                robot_id=frame.robot_id,
                index=frame.index,
                timestamp=frame.timestamp,
                data=jpeg,
                encoding=ImageEncoding.JPEG,
            )
            await self.publish(stylized_frame_topic, self._latest_frame)
            now = time.monotonic()
            if now - stats_at >= 30:
                lag = time.time() * 1000 - frame.timestamp
                self.logger.info(
                    f"Mirror: {self._frames_out / (now - stats_at):.1f} fps, "
                    f"camera-to-mirror {lag:.0f} ms, dropped {self._frames.dropped}"
                )
                self._frames_out = 0
                self._frames.dropped = 0
                stats_at = now

    # HTTP: the shutter grabs the instant frame here; /health gates compose.

    async def handle_frame(self, request: web.Request) -> web.Response:
        # ?fresh=1 (the shutter): a frame stylized after this request, even while
        # paused for a render, so a photo never shows the frozen frame.
        if request.query.get("fresh") == "1":
            asked = time.monotonic()
            self._force_until = asked + 1.5
            while self._latest_at <= asked and time.monotonic() - asked < 1.5:
                await asyncio.sleep(0.01)
        if self._latest_jpeg is None:
            return web.Response(status=503, text="No stylized frame yet")
        return web.Response(body=self._latest_jpeg, content_type="image/jpeg")

    async def handle_style(self, _: web.Request) -> web.Response:
        return web.json_response(
            {"style": self._styles.current(), "user_chosen": self._styles.user_chosen}
        )

    async def handle_health(self, _: web.Request) -> web.Response:
        if self._stylizer is None:
            return web.Response(status=503, text="Loading stylizer")
        return web.json_response({"backend": self._stylizer.backend})

    async def start_http_server(self) -> web.AppRunner:
        app = web.Application()
        app.router.add_get("/frame.jpg", self.handle_frame)
        app.router.add_get("/style", self.handle_style)
        app.router.add_get("/health", self.handle_health)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner, str(self._config.http_bind_address), self._config.http_bind_port
        )
        await site.start()
        return runner


async def main() -> None:
    config = load_config(MirrorConfig)
    service = MirrorService(config)
    runner = await service.start_http_server()
    try:
        await ServiceExecutor([service]).run()
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
