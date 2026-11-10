# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl
from workmesh.config import BaseConfig
from workmesh.messages import Robot as RobotProto


class Robot(Enum):
    """Robot name for the animation compositor service."""

    RESEARCHER = "researcher"

    def to_proto(self) -> RobotProto:
        if self == Robot.RESEARCHER:
            return RobotProto.RESEARCHER
        raise ValueError(f"Invalid robot: {self}")


class BoothAppConfig(BaseModel):
    """Where and how to reach the reachy_booth app running on the robot."""

    url: HttpUrl = Field(
        default=HttpUrl("http://reachy-mini.local:8042"),
        description=(
            "Base URL of the reachy_booth app on the robot. Use the robot's IP: "
            "mDNS names (reachy-mini.local) usually don't resolve in containers."
        ),
    )
    connect_timeout: float = Field(
        default=5.0, gt=0, description="Timeout in seconds to open the websocket."
    )
    heartbeat: float = Field(
        default=2.0,
        gt=0,
        description=(
            "Websocket ping interval in seconds. A link that misses a pong is "
            "closed and reopened, instead of silently stalling."
        ),
    )
    max_reconnect_delay: float = Field(
        default=10.0, gt=0, description="Upper bound of the reconnect backoff."
    )
    zero_on_stop: bool = Field(
        default=True,
        description="Move the robot to the zero pose when this service stops.",
    )


class RobotControllerConfig(BaseConfig):
    robot_id: Robot = Field(
        default=Robot.RESEARCHER,
        description="The ID of the robot for this robot controller.",
    )
    frame_rate_log_interval: float = Field(
        default=5.0, description="The interval in seconds to log the frame rate."
    )
    booth_app: BoothAppConfig = BoothAppConfig()
