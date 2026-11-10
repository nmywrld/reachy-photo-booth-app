"""HTTP and websocket API the photo booth's host services use.

    GET  /health               liveness + camera/motion stats (always 200 while up)
    GET  /status               present pose, in animation-frame units
    GET  /camera/stream        MJPEG live stream (reduced size, query-tunable)
    GET  /camera/frame.jpg     full-resolution still from the newest frame
    WS   /ws/motion            animation frames as JSON, newest wins
    POST /wake_up | /sleep | /zero   scripted moves (pause the motion stream)

Every blocking call (SDK, JPEG encoding) runs in a worker thread so the camera
stream and motion never wait for each other.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from collections.abc import AsyncIterator, Callable
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, StreamingResponse

from reachy_booth import __version__
from reachy_booth.camera import FrameGrabber, encode_jpeg
from reachy_booth.motion import (
    MotionController,
    measured_pose,
    parse_frame,
    pose_to_dict,
)

logger = logging.getLogger("reachy_booth.api")

BOUNDARY = "frame"
STILL_MAX_AGE_S = 2.0  # a photo must never be an old still


def register_routes(
    app: FastAPI,
    link: Any,
    grabber: FrameGrabber,
    motion: MotionController,
    stop_event: threading.Event,
) -> None:
    started_at = time.monotonic()
    move_lock = asyncio.Lock()

    def connected_robot() -> Any:
        robot = link.get()
        if robot is None:
            raise HTTPException(
                503, f"Robot daemon not connected: {link.status()['error']}"
            )
        return robot

    @app.post("/reconnect")
    async def reconnect() -> dict[str, Any]:
        link.reconnect()
        return {"success": True}

    @app.get("/health")
    async def health() -> dict[str, Any]:
        camera = grabber.stats()
        age = camera["frame_age_s"]
        return {
            "daemon": link.status(),
            "app": "reachy_booth",
            "version": __version__,
            "uptime_s": round(time.monotonic() - started_at, 1),
            "camera_ok": age is not None and age <= STILL_MAX_AGE_S,
            "camera": camera,
            "motion": motion.stats().__dict__,
        }

    @app.get("/status")
    async def status() -> dict[str, Any]:
        pose = await asyncio.to_thread(measured_pose, connected_robot())
        return {"pose": pose_to_dict(pose), "motion": motion.stats().__dict__}

    @app.get("/camera/frame.jpg")
    async def still(quality: int = Query(90, ge=1, le=100)) -> Response:
        frame = grabber.latest(STILL_MAX_AGE_S)
        if frame is None:
            raise HTTPException(503, "No fresh camera frame")
        jpeg = await asyncio.to_thread(encode_jpeg, frame, None, None, quality)
        return Response(jpeg, media_type="image/jpeg")

    @app.get("/camera/stream")
    async def stream(
        width: int = Query(640, ge=16, le=1920),
        height: int = Query(360, ge=16, le=1080),
        fps: float = Query(12.0, gt=0, le=30),
        quality: int = Query(65, ge=1, le=100),
    ) -> StreamingResponse:
        async def frames() -> AsyncIterator[bytes]:
            seq, period = 0, 1.0 / fps
            while not stop_event.is_set():
                start = time.monotonic()
                seq, frame = await asyncio.to_thread(grabber.wait_newer, seq, 1.0)
                if frame is None:
                    continue
                jpeg = await asyncio.to_thread(
                    encode_jpeg, frame, width, height, quality
                )
                yield (
                    (
                        f"--{BOUNDARY}\r\nContent-Type: image/jpeg\r\n"
                        f"Content-Length: {len(jpeg)}\r\n\r\n"
                    ).encode()
                    + jpeg
                    + b"\r\n"
                )
                # A slow client simply gets fewer frames: we always encode the newest.
                await asyncio.sleep(max(0.0, period - (time.monotonic() - start)))

        return StreamingResponse(
            frames(), media_type=f"multipart/x-mixed-replace; boundary={BOUNDARY}"
        )

    @app.websocket("/ws/motion")
    async def ws_motion(ws: WebSocket) -> None:
        await ws.accept()
        motion.client_connected()
        peer = f"{ws.client.host}:{ws.client.port}" if ws.client else "?"
        logger.info(f"Motion client connected: {peer}")
        last_error_log = 0.0
        try:
            while True:
                text = await ws.receive_text()
                try:
                    motion.set_target(parse_frame(json.loads(text)))
                except (ValueError, TypeError, AttributeError) as error:
                    now = time.monotonic()
                    if now - last_error_log > 5.0:
                        last_error_log = now
                        logger.warning(
                            f"Ignoring bad motion frame from {peer}: {error}"
                        )
        except WebSocketDisconnect:
            pass
        finally:
            motion.client_disconnected()
            logger.info(f"Motion client disconnected: {peer}")

    async def scripted_move(name: str, move: Callable[[Any], None]) -> dict[str, Any]:
        robot = connected_robot()
        if move_lock.locked():
            raise HTTPException(409, "Another move is running")
        async with move_lock:
            motion.pause()
            try:
                await asyncio.to_thread(move, robot)
            except Exception as error:
                raise HTTPException(500, f"{name} failed: {error}") from error
            finally:
                motion.resume()
        return {"success": True, "move": name}

    @app.post("/wake_up")
    async def wake_up() -> dict[str, Any]:
        return await scripted_move("wake_up", lambda r: r.wake_up())

    @app.post("/sleep")
    async def sleep() -> dict[str, Any]:
        return await scripted_move("sleep", lambda r: r.goto_sleep())

    @app.post("/zero")
    async def zero(duration: float = Query(1.5, gt=0, le=10)) -> dict[str, Any]:
        return await scripted_move(
            "zero",
            lambda r: r.goto_target(
                head=np.eye(4), antennas=[0.0, 0.0], body_yaw=0.0, duration=duration
            ),
        )
