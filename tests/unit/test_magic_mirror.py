"""Magic mirror regressions. Run: python3 -m unittest discover -s tests/unit -v.

The pure-logic and state-machine tests need only the standard library (service
methods are compiled from their AST, as in test_photo_behavior.py). Tests that
need the service's own dependencies (pydantic, protobuf, OpenCV) skip when those
are missing; run them inside the service image, e.g.:

    docker run --rm -v $PWD:/repo -w /repo -e PYTHONPATH=/repo/ui-server-service/src \
      --entrypoint python ui-server:latest -m unittest tests.unit.test_magic_mirror -v
"""

import ast
import asyncio
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, Mock

ROOT = Path(__file__).resolve().parents[2]
BOT = "interaction-manager-service/src/robots/photo_booth_bot.py"
UI_MAIN = "ui-server-service/src/main.py"


def load_module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def has(module):
    return importlib.util.find_spec(module) is not None


def load_functions(path, names, env, class_name=None):
    """Compile named (async) functions from a file, without its imports."""
    tree = ast.parse((ROOT / path).read_text())
    scope = tree
    if class_name:
        scope = next(
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.ClassDef) and n.name == class_name
        )
    found = []
    for node in ast.walk(scope):
        if (
            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            and node.name in names
        ):
            node.decorator_list = []
            found.append(node)
    module = ast.Module(
        body=[
            ast.ImportFrom(
                module="__future__", names=[ast.alias(name="annotations")], level=0
            )
        ]
        + found,
        type_ignores=[],
    )
    namespace = dict(env)
    exec(compile(ast.fix_missing_locations(module), path, "exec"), namespace)
    return {n: namespace[n] for n in names}


logic = load_module("mirror_logic", "mirror-service/src/mirror_logic.py")


class Clock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t


class StyleStateTests(unittest.TestCase):
    def make(self, clock):
        return logic.StyleState(["idle a", "idle b"], 10, 100, clock=clock)

    def test_idle_styles_rotate(self):
        clock = Clock(0)
        state = self.make(clock)
        self.assertEqual(state.current(), "idle a")
        clock.t = 10
        self.assertEqual(state.current(), "idle b")
        clock.t = 20
        self.assertEqual(state.current(), "idle a")
        self.assertFalse(state.user_chosen)

    def test_requested_style_wins_until_reset(self):
        clock = Clock(5)
        state = self.make(clock)
        state.set_user_style("  pirate,\n oil painting ")
        clock.t = 50
        self.assertEqual(state.current(), "pirate, oil painting")
        self.assertTrue(state.user_chosen)
        state.reset()  # the person walked away
        self.assertFalse(state.user_chosen)
        self.assertEqual(state.current(), "idle b")  # rotation slot at t=50

    def test_requested_style_times_out(self):
        clock = Clock(0)
        state = self.make(clock)
        state.set_user_style("anime")
        clock.t = 101
        self.assertFalse(state.user_chosen)
        self.assertIn(state.current(), ("idle a", "idle b"))

    def test_empty_style_goes_back_to_idle_and_long_styles_are_cut(self):
        state = self.make(Clock(0))
        state.set_user_style("anime")
        state.set_user_style("   ")
        self.assertFalse(state.user_chosen)
        state.set_user_style("x" * 500)
        self.assertEqual(len(state.current()), logic.MAX_STYLE_CHARS)

    def test_no_idle_styles_rejected(self):
        with self.assertRaises(ValueError):
            logic.StyleState([], 10, 100)

    def test_sd_prompt_keeps_the_style(self):
        self.assertTrue(logic.sd_prompt("anime").startswith("anime, "))


class RenderPauseTests(unittest.TestCase):
    def test_paused_until_the_render_ends(self):
        pause = logic.RenderPause(180, clock=Clock(0))
        self.assertFalse(pause.active)
        pause.started("a")
        self.assertTrue(pause.active)
        pause.ended("a")
        self.assertFalse(pause.active)

    def test_queued_renders_keep_it_paused_until_the_last(self):
        pause = logic.RenderPause(180, clock=Clock(0))
        pause.started("a")
        pause.started("b")  # second photo while the first renders
        pause.ended("a")
        self.assertTrue(pause.active)
        pause.ended("b")
        self.assertFalse(pause.active)

    def test_lost_end_message_times_out(self):
        clock = Clock(0)
        pause = logic.RenderPause(180, clock=clock)
        pause.started("a")
        clock.t = 179
        self.assertTrue(pause.active)
        clock.t = 181
        self.assertFalse(pause.active)

    def test_unknown_end_is_ignored(self):
        pause = logic.RenderPause(180, clock=Clock(0))
        pause.ended("cancelled-shutter")  # FAILED before any render started
        self.assertFalse(pause.active)


class LatestSlotTests(unittest.IsolatedAsyncioTestCase):
    async def test_slow_consumer_gets_only_the_newest_frame(self):
        slot = logic.LatestSlot()
        for i in range(5):
            slot.put(i)
        self.assertEqual(await slot.get(), 4)
        self.assertEqual(slot.dropped, 4)

    async def test_get_waits_for_the_next_frame(self):
        slot = logic.LatestSlot()
        getter = asyncio.create_task(slot.get())
        await asyncio.sleep(0)
        self.assertFalse(getter.done())
        slot.put("frame")
        self.assertEqual(await asyncio.wait_for(getter, 1), "frame")


class Status:
    TOOL_CALL_STARTED, TOOL_CALL_COMPLETED, TOOL_CALL_FAILED = 0, 1, 2


def bot_env(**extra):
    env = dict(
        asyncio=asyncio,
        json=json,
        time=__import__("time"),
        uuid=__import__("uuid"),
        ToolStatus=Mock(side_effect=lambda **k: NS(**k), Status=Status),
        ImageGeneration=lambda **k: NS(**k),
        LightEffect=lambda **k: NS(**k),
        StaticAnimation="static",
        Color=NS(WHITE="white", GRAY="gray"),
        tool_status_topic="tool_status",
        mirror_capture_topic="mirror_capture",
        MIRROR_PHOTO_TOOL="mirror_photo",
        Awaitable=object,
        Any=object,
    )
    env.update(extra)
    return env


def make_bot(ready=True):
    tasks = []
    service = NS(publish=AsyncMock(), create_task=Mock(side_effect=tasks.append))
    bot = NS(
        shutter_lock=asyncio.Lock(),
        robot_name="BOT",
        _logger=Mock(),
        _service=service,
        tasks=tasks,
        config=NS(shutter_timeout=5, mirror_countdown_seconds=0),
        light_manager=NS(
            light_off=AsyncMock(), light_on=AsyncMock(), light_blink=AsyncMock()
        ),
        handle_talking=AsyncMock(),
    )

    async def wait_for_photo_subject():
        if not ready:
            raise TimeoutError

    def require_photo_subject():
        if not ready:
            raise RuntimeError("Photo cancelled: no recently detected person")

    def hang_forever(**_):
        # Compositor down: clips never start. A bare future never resolves.
        return asyncio.get_running_loop().create_future()

    bot.wait_for_photo_subject = wait_for_photo_subject
    bot.require_photo_subject = require_photo_subject
    bot.play_and_wait = hang_forever
    return bot


class ShutterTests(unittest.IsolatedAsyncioTestCase):
    NAMES = [
        "handle_mirror_shutter",
        "handle_mirror_countdown",
        "request_mirror_capture",
        "_best_effort",
    ]

    def bind(self, bot):
        fns = load_functions(BOT, self.NAMES, bot_env())
        for name in self.NAMES:
            setattr(bot, name, fns[name].__get__(bot))
        return bot

    async def test_shutter_captures_even_if_robot_animations_hang(self):
        bot = self.bind(make_bot(ready=True))
        await asyncio.wait_for(bot.handle_mirror_shutter(), 2)
        topic, message = bot._service.publish.await_args.args
        self.assertEqual(topic, "mirror_capture")
        self.assertTrue(message.action_uuid)
        bot.light_manager.light_blink.assert_awaited_once()  # flash
        bot.handle_talking.assert_not_called()
        for task in bot.tasks:  # animations were handed off, not awaited
            task.close()

    async def test_hanging_animation_is_abandoned(self):
        bot = self.bind(make_bot())
        await asyncio.wait_for(bot._best_effort(bot.play_and_wait(), timeout=0.05), 1)
        bot._logger.warning.assert_called_once()

    async def test_no_person_cancels_and_tells_the_ui(self):
        bot = self.bind(make_bot(ready=False))
        await bot.handle_mirror_shutter()
        topic, message = bot._service.publish.await_args.args
        self.assertEqual(topic, "tool_status")
        self.assertEqual(
            (message.name, message.status), ("mirror_photo", Status.TOOL_CALL_FAILED)
        )
        self.assertIn("No one", json.loads(message.response)["error"])
        bot.light_manager.light_blink.assert_not_awaited()
        self.assertEqual(len(bot.tasks), 1)  # the spoken hint
        bot.tasks[0].close()

    async def test_second_press_during_a_photo_is_ignored(self):
        bot = self.bind(make_bot(ready=True))
        async with bot.shutter_lock:
            await bot.handle_mirror_shutter()
        bot._service.publish.assert_not_awaited()
        bot.light_manager.light_on.assert_not_awaited()


class PresenceTests(unittest.IsolatedAsyncioTestCase):
    """With detection always on, nobody re-announces a person already there."""

    async def test_search_keeps_presence_only_when_detection_is_always_on(self):
        find_user = load_functions(BOT, ["find_user"], {})["find_user"]
        for always_on, still_found in ((True, True), (False, False)):
            event = asyncio.Event()
            event.set()
            bot = NS(
                _logger=Mock(),
                robot_name="BOT",
                user_found_event=event,
                config=NS(presence_always_on=always_on),
            )
            await find_user(bot)
            self.assertEqual(event.is_set(), still_found)


class UiPhotoStateTests(unittest.IsolatedAsyncioTestCase):
    """The kiosk's view of a shutter photo, from `mirror_photo` tool statuses."""

    NAMES = ["_public_url", "_later", "shutter_pressed", "update_mirror_photo"]

    def make_state(self):
        from urllib.parse import urlparse

        Tool = NS(Status=Status)
        fns = load_functions(
            UI_MAIN,
            self.NAMES,
            dict(
                json=json,
                asyncio=asyncio,
                urlparse=urlparse,
                HttpUrl=str,
                ToolStatus=Tool,
                MirrorPhoto=lambda **k: NS(
                    **{
                        "hires_image": None,
                        "qr_code": None,
                        "status": "processing",
                        **k,
                    }
                ),
                Callable=object,
                Awaitable=object,
                AppState=object,
            ),
            class_name="State",
        )
        state = NS(
            minio_host="kiosk:9010",
            photo_display_seconds=60,
            shutter_timeout_seconds=30,
            photo_task=None,
            shutter_task=None,
            state=NS(mirror_photo=None, shutter_busy=False),
        )
        for name, fn in fns.items():
            setattr(state, name, fn.__get__(state))
        return state

    def tool(self, status, uuid="a", **data):
        return NS(status=status, action_uuid=uuid, response=json.dumps(data))

    async def test_instant_then_hires(self):
        state = self.make_state()
        cb = AsyncMock()
        self.assertTrue(state.shutter_pressed(cb))
        self.assertFalse(state.shutter_pressed(cb))  # busy until the photo arrives
        await state.update_mirror_photo(
            self.tool(
                Status.TOOL_CALL_STARTED,
                image_url="http://minio:9010/b/i.png",
                qrcode_url="http://minio:9010/b/q.png",
            ),
            cb,
        )
        photo = state.state.mirror_photo
        self.assertEqual(photo.instant_image, "http://kiosk:9010/b/i.png")
        self.assertEqual(photo.qr_code, "http://kiosk:9010/b/q.png")
        self.assertFalse(state.state.shutter_busy)
        await state.update_mirror_photo(
            self.tool(
                Status.TOOL_CALL_COMPLETED, image_url="http://minio:9010/b/h.png"
            ),
            cb,
        )
        self.assertEqual(
            (photo.hires_image, photo.status), ("http://kiosk:9010/b/h.png", "ready")
        )
        state.photo_task.cancel()

    async def test_render_for_an_old_photo_is_ignored(self):
        state = self.make_state()
        cb = AsyncMock()
        await state.update_mirror_photo(
            self.tool(Status.TOOL_CALL_STARTED, uuid="new", image_url="http://m/i.png"),
            cb,
        )
        result = await state.update_mirror_photo(
            self.tool(
                Status.TOOL_CALL_COMPLETED, uuid="old", image_url="http://m/h.png"
            ),
            cb,
        )
        self.assertIsNone(result)
        self.assertIsNone(state.state.mirror_photo.hires_image)
        state.photo_task.cancel()

    async def test_cancelled_shutter_releases_the_button(self):
        state = self.make_state()
        cb = AsyncMock()
        state.shutter_pressed(cb)
        await state.update_mirror_photo(
            self.tool(Status.TOOL_CALL_FAILED, error="No one in front of the mirror"),
            cb,
        )
        self.assertFalse(state.state.shutter_busy)
        self.assertIsNone(state.state.mirror_photo)


@unittest.skipUnless(has("pydantic"), "needs pydantic (run in the ui-server image)")
class UiMessageTests(unittest.TestCase):
    def test_shutter_message_parses(self):
        sys.path.insert(0, str(ROOT / "ui-server-service/src"))
        try:
            messages = load_module("ui_messages", "ui-server-service/src/messages.py")
        finally:
            sys.path.pop(0)
        parsed = messages.BaseMessage.model_validate_json(
            '{"message_type": "ShutterMessage"}'
        )
        self.assertIsInstance(parsed.root, messages.ShutterMessage)
        state = messages.AppState(tracking_data=[])
        self.assertFalse(state.user_present or state.shutter_busy)
        self.assertIsNone(state.mirror_photo)


@unittest.skipUnless(has("cv2") and has("google.protobuf"), "needs OpenCV + protobuf")
class FrameSourceTests(unittest.TestCase):
    def setUp(self):
        import cv2
        import numpy as np

        self.cv2, self.np = cv2, np
        track = load_module("camera_track", "ui-server-service/src/camera_track.py")
        self.FrameSource = track.FrameSource

    def frame(self, w, h, value):
        ok, data = self.cv2.imencode(
            ".jpg", self.np.full((h, w, 3), value, self.np.uint8)
        )
        return NS(data=data.tobytes())

    def test_mirror_preferred_raw_fallback_fixed_size(self):
        clock = Clock(0)
        source = self.FrameSource(size=512, fallback_after=1.0, clock=clock)
        self.assertEqual(source.current().shape, (512, 512, 3))  # black until frames
        source.update(self.frame(640, 360, 50), stylized=False)
        source.update(self.frame(512, 512, 200), stylized=True)
        self.assertGreater(source.current().mean(), 150)  # mirror wins
        clock.t = 2.0  # mirror silent for 2 s
        image = source.current()
        self.assertEqual(image.shape, (512, 512, 3))  # raw, cropped to the same size
        self.assertLess(image.mean(), 100)


if __name__ == "__main__":
    unittest.main()
