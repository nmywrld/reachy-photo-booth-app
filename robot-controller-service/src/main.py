# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Forward the booth's robot frames to the reachy_booth app on the robot.

The robot runs the reachy_booth app (``reachy_booth/`` in this repository),
which drives the motors through the Reachy Mini Python SDK on the robot itself.
This service subscribes to ``robot_frame`` and sends the newest frame over one
websocket. The control loop, rate limiting and unit conversion happen on the
robot, so Wi-Fi delays add lag but never queue stale frames or break motion.
"""

import asyncio
import contextlib
import json
import time
from typing import Any, override

import aiohttp
from configuration import RobotControllerConfig
from google.protobuf.json_format import MessageToDict
from workmesh.messages import AnimationFrame, RobotFrame
from workmesh.service import subscribe
from workmesh.service_executor import ServiceExecutor

from workmesh import Service, load_config, robot_frame_topic


def frame_to_dict(frame: AnimationFrame) -> dict[str, Any]:
    """AnimationFrame -> the JSON object reachy_booth's /ws/motion expects.

    Zero-valued fields are omitted, as protobuf JSON does; the app reads a
    missing field as 0.
    """
    return MessageToDict(frame, preserving_proto_field_name=True)


class RobotService(Service):
    def __init__(self, config: RobotControllerConfig) -> None:
        super().__init__(config)

        self.config = config
        self.robot_id = config.robot_id
        self.base_url = str(config.booth_app.url).rstrip("/")
        self.ws_url = self.base_url.replace("http", "ws", 1) + "/ws/motion"

        # Start time: frames older than the service are ignored.
        self.start_time: int = int(time.time() * 1000)

        # Newest frame not yet sent; the sender always takes the latest one.
        self._latest: dict[str, Any] | None = None
        self._new_frame = asyncio.Event()
        self._connected = False
        self.stop_event: asyncio.Event = asyncio.Event()

        # Frame rate tracking
        self.frame_timestamps: list[float] = []
        self.last_framerate_log_time: float = time.time()
        self.frames_sent = 0

        self.sender_task = self.create_task(self._send_loop())
        self.logger.info(f"Forwarding robot frames to {self.ws_url}")

    @override
    async def stop(self) -> None:
        self.stop_event.set()
        self.sender_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self.sender_task
        if self.config.booth_app.zero_on_stop:
            await self._go_to_zero_pose()
        await super().stop()

    async def _go_to_zero_pose(self, duration: float = 2.0) -> None:
        self.logger.info("Going to zero pose...")
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.base_url}/zero",
                    params={"duration": str(duration)},
                    timeout=aiohttp.ClientTimeout(total=duration + 5),
                ) as resp,
            ):
                resp.raise_for_status()
        except (aiohttp.ClientError, TimeoutError) as error:
            self.logger.warning(f"Could not move Reachy to zero pose: {error}")

    async def _send_loop(self) -> None:
        """Keep one websocket open to the robot and send the newest frame."""
        booth = self.config.booth_app
        delay, outage = 1.0, None
        # Bound the connection attempt; once open, the heartbeat detects a dead link.
        timeout = aiohttp.ClientTimeout(total=None, connect=booth.connect_timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while not self.stop_event.is_set():
                try:
                    async with session.ws_connect(
                        self.ws_url,
                        heartbeat=booth.heartbeat,
                        timeout=aiohttp.ClientWSTimeout(ws_close=booth.connect_timeout),
                    ) as ws:
                        self._connected, delay, outage = True, 1.0, None
                        self.logger.info("Connected to the reachy_booth app")
                        await self._pump(ws)
                    reason = "connection closed"
                except asyncio.CancelledError:
                    raise
                except (aiohttp.ClientError, ConnectionError, TimeoutError) as error:
                    reason = str(error) or type(error).__name__
                finally:
                    self._connected = False
                if self.stop_event.is_set():
                    break
                if reason != outage:
                    self.logger.warning(
                        f"Reachy link down ({reason}); retrying. Is the "
                        f"reachy_booth app running at {self.base_url}?"
                    )
                    outage = reason
                await asyncio.sleep(delay)
                delay = min(delay * 2, booth.max_reconnect_delay)

    async def _pump(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        """Send frames until the socket closes. A reader task handles pongs."""

        async def drain() -> None:
            async for _ in ws:  # the app sends nothing; this processes pongs
                pass

        reader = asyncio.create_task(drain())
        try:
            # Send the frame that arrived while disconnected, if any.
            if self._latest is not None:
                self._new_frame.set()
            while not reader.done():
                try:
                    await asyncio.wait_for(self._new_frame.wait(), timeout=1.0)
                except TimeoutError:
                    continue
                self._new_frame.clear()
                frame = self._latest
                if frame is not None:
                    await ws.send_str(json.dumps(frame))
                    self.frames_sent += 1
        finally:
            reader.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await reader

    @subscribe(robot_frame_topic)
    async def on_robot_frame_topic(self, message: RobotFrame):
        # Ignore all messages if the service is stopping
        if self.stop_event.is_set():
            return

        if message.timestamp < self.start_time:
            self.logger.debug("Skipping message. Message is older than the service.")
            return

        # Check if the message is for this robot
        if message.robot_id != self.robot_id.to_proto():
            return

        # Track frame rate
        current_time = time.time()
        self.frame_timestamps.append(current_time)

        # Log average frame rate every X seconds
        time_since_last_log = current_time - self.last_framerate_log_time
        if time_since_last_log >= self.config.frame_rate_log_interval:
            if len(self.frame_timestamps) > 1:
                time_span = self.frame_timestamps[-1] - self.frame_timestamps[0]
                if time_span > 0:
                    avg_fps = (len(self.frame_timestamps) - 1) / time_span
                    link = "up" if self._connected else "down"
                    self.logger.debug(
                        f"Average frame rate: {avg_fps:.2f} FPS (over {time_span:.1f}s,"
                        f" {len(self.frame_timestamps)} frames), sent "
                        f"{self.frames_sent}, link {link}"
                    )

            # Reset tracking
            self.frame_timestamps.clear()
            self.last_framerate_log_time = current_time

        self.logger.debug(f"Message position: {message.frame}")
        self._latest = frame_to_dict(message.frame)
        self._new_frame.set()


async def main():
    config = load_config(RobotControllerConfig)
    await ServiceExecutor([RobotService(config)]).run()


if __name__ == "__main__":
    asyncio.run(main())
