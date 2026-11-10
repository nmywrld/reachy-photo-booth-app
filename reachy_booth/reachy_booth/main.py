"""Reachy Booth: the on-robot half of the Reachy photo booth.

Runs on the wireless Reachy Mini and talks to the daemon through the Python SDK
on localhost, so motion control and camera capture never cross Wi-Fi. The
photo booth's host services reach it over HTTP/websocket on port 8042 (see
``api.py``); only small motion frames and JPEGs travel over the network.

Like the Reachy Mini testbench, the app overrides ``wrapped_run`` instead of
letting the base class connect once and die on failure: the web server starts
first, and the daemon connection is made (and re-made) in the background by
``RobotLink``. ``/health`` always answers and says whether the daemon is
connected.
"""

import contextlib
import logging
import threading
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from reachy_mini import ReachyMini, ReachyMiniApp

from reachy_booth.api import register_routes
from reachy_booth.camera import FrameGrabber
from reachy_booth.link import RobotLink
from reachy_booth.motion import MotionController

PORT = 8042
STATIC_DIR = Path(__file__).parent / "static"

logger = logging.getLogger("reachy_booth")


def build_app() -> FastAPI:
    app = FastAPI(title="Reachy Booth")

    @app.middleware("http")
    async def no_cache(request, call_next) -> Response:  # type: ignore[no-untyped-def]
        response: Response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

        @app.get("/")
        async def index() -> FileResponse:
            return FileResponse(STATIC_DIR / "index.html")

    return app


class ReachyBooth(ReachyMiniApp):
    # Shown by the dashboard as the app's settings page.
    custom_app_url: str | None = f"http://0.0.0.0:{PORT}"
    # We serve our own FastAPI app, as the testbench does.
    dont_start_webserver: bool = True

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        """Required by the base class; unused: see ``wrapped_run``."""

    def wrapped_run(self, *args: object, **kwargs: object) -> None:
        logging.getLogger("reachy_booth").setLevel(logging.INFO)
        stop_event = self.stop_event

        link = RobotLink(stop_event)
        grabber = FrameGrabber(link, stop_event)
        motion = MotionController(link, stop_event)
        app = build_app()
        register_routes(app, link, grabber, motion, stop_event)

        server = uvicorn.Server(
            uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="warning")
        )
        server_thread = threading.Thread(target=server.run, name="booth-http")
        server_thread.start()
        link.start()
        grabber.start()
        motion.start()
        logger.info(f"Reachy Booth serving on port {PORT}; connecting to the daemon")

        try:
            stop_event.wait()
        finally:
            stop_event.set()
            server.should_exit = True
            server_thread.join(timeout=5)
            motion.join(timeout=2)
            grabber.join(timeout=2)
            link.join(timeout=5)
            robot = link.get()
            if robot is not None:
                with contextlib.suppress(Exception):
                    robot.client.disconnect()


if __name__ == "__main__":
    booth = ReachyBooth()
    try:
        booth.wrapped_run()
    except KeyboardInterrupt:
        booth.stop()
