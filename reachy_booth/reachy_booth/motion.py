"""Motion streaming for the photo booth.

The photo booth's animation compositor (on the host) produces animation frames
at ~30 Hz. The host's robot-controller forwards the newest one over a websocket
and this module turns it into robot motion, entirely on the robot:

* one control thread, the only place calling ``set_target()``, at a fixed rate
  (see the SDK's control-loop guidance);
* the newest frame wins: a Wi-Fi stall never queues stale frames, and while no
  new frame arrives the robot holds the last target;
* every joint is rate limited from the last *commanded* pose, so a jump in the
  target (e.g. after the link comes back) becomes a smooth catch-up move.

Frame units follow the booth's ``AnimationFrame`` message: angles in degrees,
head translation in centimetres.
"""

from __future__ import annotations

import logging
import math
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np
import numpy.typing as npt

logger = logging.getLogger("reachy_booth.motion")

# Order of the values in a pose vector.
JOINTS = (
    "body_angle",
    "r_antenna_angle",
    "l_antenna_angle",
    "head_position_x",
    "head_position_y",
    "head_position_z",
    "roll",
    "pitch",
    "yaw",
)
ROTATION_SLICE = slice(6, 9)

# Maximum speed per joint, in frame units per second. They only cap spikes and
# catch-up moves: normal booth animations stay well below them.
DEFAULT_MAX_SPEED = np.array(
    [
        180.0,  # body_angle, deg/s
        900.0,  # r_antenna_angle, deg/s
        900.0,  # l_antenna_angle, deg/s
        15.0,  # head_position_x, cm/s
        15.0,  # head_position_y, cm/s
        15.0,  # head_position_z, cm/s
        360.0,  # roll, deg/s
        360.0,  # pitch, deg/s
        360.0,  # yaw, deg/s
    ]
)


def parse_frame(data: Mapping[str, Any]) -> npt.NDArray[np.float64]:
    """Turn an animation frame (JSON object) into a pose vector.

    Missing fields default to 0, like an unset protobuf field. Raises
    ``ValueError`` for non-numeric or non-finite values.
    """
    rotation = data.get("head_rotation") or {}
    if not isinstance(rotation, Mapping):
        raise ValueError("head_rotation must be an object")
    values = [
        data.get("body_angle", 0.0),
        data.get("r_antenna_angle", 0.0),
        data.get("l_antenna_angle", 0.0),
        data.get("head_position_x", 0.0),
        data.get("head_position_y", 0.0),
        data.get("head_position_z", 0.0),
        rotation.get("roll", 0.0),
        rotation.get("pitch", 0.0),
        rotation.get("yaw", 0.0),
    ]
    try:
        pose = np.array([float(v) for v in values], dtype=np.float64)
    except (TypeError, ValueError) as error:
        raise ValueError(f"frame values must be numbers: {error}") from error
    if not np.all(np.isfinite(pose)):
        raise ValueError("frame values must be finite")
    return pose


def step_towards(
    current: npt.NDArray[np.float64],
    target: npt.NDArray[np.float64],
    dt: float,
    max_speed: npt.NDArray[np.float64] = DEFAULT_MAX_SPEED,
) -> npt.NDArray[np.float64]:
    """Move ``current`` towards ``target`` by at most ``max_speed * dt`` per joint.

    Head rotations take the short way round (deltas wrapped to [-180, 180]).
    """
    delta = target - current
    rot = delta[ROTATION_SLICE]
    delta[ROTATION_SLICE] = (rot + 180.0) % 360.0 - 180.0
    limit = max_speed * max(dt, 0.0)
    return current + np.clip(delta, -limit, limit)


def pose_to_targets(
    pose: npt.NDArray[np.float64],
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], float]:
    """Convert a pose vector into ``set_target(head, antennas, body_yaw)`` args."""
    from reachy_mini.utils import create_head_pose

    body, r_ant, l_ant, x, y, z, roll, pitch, yaw = pose
    head = create_head_pose(
        x=x * 10.0,  # cm -> mm
        y=y * 10.0,
        z=z * 10.0,
        roll=roll,
        pitch=pitch,
        yaw=yaw,
        mm=True,
        degrees=True,
    )
    antennas = np.deg2rad([r_ant, l_ant])
    return head, antennas, float(np.deg2rad(body))


def measured_pose(reachy_mini: Any) -> npt.NDArray[np.float64]:
    """Read the robot's present pose as a pose vector (frame units)."""
    from reachy_mini.utils.rotation import Rotation

    head_joints, antenna_joints = reachy_mini.get_current_joint_positions()
    head = np.asarray(reachy_mini.get_current_head_pose(), dtype=np.float64)
    roll, pitch, yaw = Rotation.from_matrix(head[:3, :3]).as_euler("xyz", degrees=True)
    x, y, z = head[:3, 3] * 100.0  # m -> cm
    return np.array(
        [
            math.degrees(head_joints[0]),
            math.degrees(antenna_joints[0]),
            math.degrees(antenna_joints[1]),
            x,
            y,
            z,
            roll,
            pitch,
            yaw,
        ],
        dtype=np.float64,
    )


def pose_to_dict(pose: npt.NDArray[np.float64]) -> dict[str, Any]:
    """Pose vector -> animation-frame-shaped dict (for status endpoints)."""
    values = [round(float(v), 3) for v in pose]
    frame: dict[str, Any] = dict(zip(JOINTS[:6], values[:6], strict=True))
    frame["head_rotation"] = dict(zip(JOINTS[6:], values[6:], strict=True))
    return frame


class Robot(Protocol):
    """The part of ``ReachyMini`` the controller uses."""

    def set_target(self, head: Any, antennas: Any, body_yaw: float) -> None: ...
    def get_current_joint_positions(self) -> tuple[list[float], list[float]]: ...
    def get_current_head_pose(self) -> Any: ...


@dataclass
class MotionStats:
    clients: int
    frames_received: int
    last_frame_age_s: float | None
    streaming: bool
    paused: bool


class MotionController:
    """Owns ``set_target()``: streams the newest booth frame to the robot."""

    def __init__(
        self,
        link: Any,
        stop_event: threading.Event,
        rate_hz: float = 50.0,
        max_speed: npt.NDArray[np.float64] = DEFAULT_MAX_SPEED,
    ) -> None:
        self._link = link  # .get() -> connected robot, or None
        self._stop = stop_event
        self._period = 1.0 / rate_hz
        self._max_speed = max_speed

        self._lock = threading.Lock()
        self._target: npt.NDArray[np.float64] | None = None
        self._target_at = 0.0
        self._frames = 0
        self._clients = 0
        self._paused = 0  # >0 while a scripted move (goto) owns the robot

        self._commanded: npt.NDArray[np.float64] | None = None
        self._last_error_log = 0.0
        self._thread = threading.Thread(
            target=self._loop, name="booth-motion", daemon=True
        )

    # ----------------------------------------------------------- inputs

    def start(self) -> None:
        self._thread.start()

    def join(self, timeout: float | None = None) -> None:
        self._thread.join(timeout)

    def set_target(self, pose: npt.NDArray[np.float64]) -> None:
        """Newest frame from the host; replaces any frame not yet applied."""
        with self._lock:
            self._target = pose
            self._target_at = time.monotonic()
            self._frames += 1

    def client_connected(self) -> None:
        with self._lock:
            self._clients += 1

    def client_disconnected(self) -> None:
        with self._lock:
            self._clients = max(0, self._clients - 1)

    def pause(self) -> None:
        """Stop streaming while a scripted move runs (wake up, sleep, zero)."""
        with self._lock:
            self._paused += 1

    def resume(self) -> None:
        """Resume streaming from the robot's present pose, not the old target.

        The old target is dropped so the robot stays where the scripted move
        left it until the host sends a new frame.
        """
        with self._lock:
            self._paused = max(0, self._paused - 1)
            if self._paused == 0:
                self._target = None
                self._commanded = None

    def stats(self) -> MotionStats:
        with self._lock:
            age = time.monotonic() - self._target_at if self._target_at else None
            return MotionStats(
                clients=self._clients,
                frames_received=self._frames,
                last_frame_age_s=None if age is None else round(age, 3),
                streaming=self._target is not None and not self._paused,
                paused=self._paused > 0,
            )

    # ----------------------------------------------------------- loop

    def _loop(self) -> None:
        last_tick = time.monotonic()
        while not self._stop.is_set():
            tick = time.monotonic()
            dt, last_tick = tick - last_tick, tick
            try:
                self._step(dt)
            except Exception as error:  # keep the loop alive; log at most 1/s
                if tick - self._last_error_log > 1.0:
                    self._last_error_log = tick
                    logger.warning(f"Motion step failed: {error}")
            self._stop.wait(max(0.0, self._period - (time.monotonic() - tick)))

    def _step(self, dt: float) -> None:
        robot = self._link.get()
        with self._lock:
            if robot is None:  # daemon unreachable: restart from the real pose
                self._commanded = None
                return
            if self._paused or self._target is None:
                return
            target = self._target.copy()
            commanded = self._commanded
        if commanded is None:
            # First frame (or first after a scripted move): start from where
            # the robot really is, so the rate limit applies to the first move.
            commanded = measured_pose(robot)
        commanded = step_towards(commanded, target, dt, self._max_speed)
        head, antennas, body_yaw = pose_to_targets(commanded)
        with self._lock:
            if self._paused:  # a goto started while we computed
                return
            self._commanded = commanded
        robot.set_target(head=head, antennas=antennas, body_yaw=body_yaw)
