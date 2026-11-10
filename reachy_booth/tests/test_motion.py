"""Unit tests for the motion logic (no robot needed).

Run from the app folder:  python -m pytest tests
"""

import threading
import time

import numpy as np
import pytest
from reachy_booth.link import FixedLink, RobotLink
from reachy_booth.motion import (
    DEFAULT_MAX_SPEED,
    MotionController,
    parse_frame,
    pose_to_dict,
    step_towards,
)

FRAME = {
    "body_angle": 10.0,
    "r_antenna_angle": -20.0,
    "l_antenna_angle": 20.0,
    "head_position_x": 0.5,
    "head_position_y": -0.5,
    "head_position_z": 1.0,
    "head_rotation": {"roll": 1.0, "pitch": -2.0, "yaw": 3.0},
}


def test_parse_frame_roundtrip() -> None:
    pose = parse_frame(FRAME)
    assert pose_to_dict(pose) == FRAME


def test_parse_frame_defaults_missing_fields_to_zero() -> None:
    assert np.all(parse_frame({}) == 0.0)


@pytest.mark.parametrize(
    "bad",
    [{"body_angle": "x"}, {"body_angle": float("nan")}, {"head_rotation": [1, 2]}],
)
def test_parse_frame_rejects_bad_values(bad: dict) -> None:
    with pytest.raises(ValueError):
        parse_frame(bad)


def test_step_towards_limits_each_joint() -> None:
    current = np.zeros(9)
    target = np.full(9, 1000.0)
    stepped = step_towards(current, target, dt=0.1)
    # Rotation deltas wrap to [-180, 180]: 1000 deg is -80 deg the short way.
    expected = DEFAULT_MAX_SPEED * 0.1
    expected[6:] = -expected[6:]
    assert np.allclose(stepped, expected)


def test_step_towards_reaches_close_targets_exactly() -> None:
    current = np.zeros(9)
    target = np.full(9, 0.01)
    assert np.allclose(step_towards(current, target, dt=0.02), target)


def test_step_towards_takes_short_way_round() -> None:
    current = np.zeros(9)
    current[8] = 170.0  # yaw
    target = current.copy()
    target[8] = -170.0
    stepped = step_towards(current, target, dt=1.0)
    assert stepped[8] == pytest.approx(190.0)  # +20 deg, not -340 deg


class FakeRobot:
    def __init__(self) -> None:
        self.targets: list[tuple] = []

    def set_target(self, head, antennas, body_yaw) -> None:
        self.targets.append((np.array(head), np.array(antennas), body_yaw))

    def get_current_joint_positions(self):
        return [0.0] * 7, [0.0, 0.0]

    def get_current_head_pose(self):
        return np.eye(4)


def test_controller_streams_latest_frame_and_pauses() -> None:
    robot, stop = FakeRobot(), threading.Event()
    controller = MotionController(FixedLink(robot), stop, rate_hz=100)
    controller.start()
    try:
        time.sleep(0.05)
        assert robot.targets == []  # nothing sent before the first frame

        controller.set_target(parse_frame({"r_antenna_angle": 30.0}))
        time.sleep(0.3)  # 30 deg at 900 deg/s takes ~0.03 s
        _, antennas, _ = robot.targets[-1]
        assert np.rad2deg(antennas[0]) == pytest.approx(30.0)

        controller.pause()
        time.sleep(0.05)
        count = len(robot.targets)
        time.sleep(0.1)
        assert len(robot.targets) == count  # paused: no set_target
        controller.resume()
        time.sleep(0.1)
        assert len(robot.targets) == count  # old target dropped on resume
        assert not controller.stats().streaming
    finally:
        stop.set()
        controller.join(timeout=1)


def test_link_retries_until_the_daemon_is_reachable() -> None:
    stop, attempts = threading.Event(), []

    class Robot:
        class client:  # noqa: N801
            _is_alive = True

            @staticmethod
            def disconnect() -> None:
                pass

    def connect():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("daemon busy")
        return Robot()

    link = RobotLink(stop, connect=connect, retry_delay=0.01)
    link.start()
    try:
        deadline = time.monotonic() + 3
        while link.get() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        assert link.get() is not None
        assert link.status()["connected"] and link.status()["error"] is None
        link.reconnect()  # drops and reconnects without raising
        deadline = time.monotonic() + 3
        while link.get() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        assert link.get() is not None
    finally:
        stop.set()
        link.join(timeout=2)
