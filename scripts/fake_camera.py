# SPDX-License-Identifier: Apache-2.0
"""Stand-in for camera-service when the robot is offline: test the magic mirror.

Publishes `camera_frame` (640x360 JPEG, gently moving so frames differ) from a
still image or a video file, and serves GET /capture (1280x720) like the real
camera. Run it in the camera image, in place of the camera container:

    docker compose stop camera && docker rm camera
    docker run --rm -d --name camera --hostname camera --network <project>_default \
      -p 7071:7071 -v $PWD/scripts:/scripts:ro -v /path/to/person.jpg:/person.jpg:ro \
      --entrypoint python camera:latest /scripts/fake_camera.py /person.jpg

`docker compose up -d camera` brings the real camera back.
"""

import argparse
import asyncio
import math
import time

import cv2
import numpy as np
from aiohttp import web
from workmesh.messages import Frame, ImageEncoding, Robot
from workmesh.service import Producer

from workmesh import camera_frame_topic


def letterbox(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """Fit the whole image into width x height on grey, like a centred person."""
    scale = min(width / image.shape[1], height / image.shape[0])
    w, h = int(image.shape[1] * scale), int(image.shape[0] * scale)
    canvas = np.full((height, width, 3), 128, np.uint8)
    y, x = (height - h) // 2, (width - w) // 2
    canvas[y : y + h, x : x + w] = cv2.resize(image, (w, h))
    return canvas


class Source:
    def __init__(self, path: str) -> None:
        self.still = cv2.imread(path)
        self.video = None if self.still is not None else cv2.VideoCapture(path)
        if self.still is None and not self.video.isOpened():  # type: ignore[union-attr]
            raise SystemExit(f"Cannot read {path}")

    def frame(self, t: float, width: int, height: int) -> np.ndarray:
        if self.video is not None:
            ok, image = self.video.read()
            if not ok:
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, image = self.video.read()
            return letterbox(image, width, height)
        base = letterbox(self.still, int(width * 1.06), int(height * 1.06))
        dx = int((base.shape[1] - width) / 2 * (1 + math.sin(t / 2)))
        dy = int((base.shape[0] - height) / 2 * (1 + math.cos(t / 3)))
        return base[dy : dy + height, dx : dx + width]


async def publish(source: Source, fps: float) -> None:
    async with Producer() as producer:
        index = 0
        while True:
            start = time.monotonic()
            index += 1
            image = source.frame(time.time(), 640, 360)
            ok, data = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 65])
            await producer.publish(
                camera_frame_topic,
                Frame(
                    robot_id=Robot.RESEARCHER,
                    index=index,
                    timestamp=int(time.time() * 1000),
                    data=data.tobytes(),
                    encoding=ImageEncoding.JPEG,
                ),
            )
            await asyncio.sleep(max(0.0, 1 / fps - (time.monotonic() - start)))


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="image or video file")
    parser.add_argument("--fps", type=float, default=15)
    args = parser.parse_args()
    source = Source(args.source)

    async def capture(_: web.Request) -> web.Response:
        image = source.frame(time.time(), 1280, 720)
        ok, data = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return web.Response(body=data.tobytes(), content_type="image/jpeg")

    app = web.Application()
    app.router.add_get("/capture", capture)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 7071).start()
    print(
        f"Fake camera: {args.source} at {args.fps} fps, /capture on :7071", flush=True
    )
    await publish(source, args.fps)


if __name__ == "__main__":
    asyncio.run(main())
