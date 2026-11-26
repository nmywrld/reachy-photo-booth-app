# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, RootModel

COLOR = Literal[
    "TRANSPARENT",
    "GRAY",
    "WHITE",
    "BLUE",
    "INTENSE_BLUE",
    "GREEN",
    "INTENSE_GREEN",
    "RED",
    "INTENSE_RED",
]


class BoundingCircle(BaseModel):
    center_x: float
    center_y: float
    radius: float
    is_primary: bool


class Transcript(BaseModel):
    text: str
    author: Literal["Bot", "User"]
    id: str | None = None


class StaticAnimation(BaseModel):
    type: Literal["Static"] = "Static"
    color: COLOR
    in_transition: float


class FillCircleAnimation(BaseModel):
    type: Literal["FillCircle"] = "FillCircle"
    primary_color: COLOR
    secondary_color: COLOR
    in_transition: float
    duration: float


class AskHuman(BaseModel):
    type: Literal["AskHuman"] = "AskHuman"


class GreetUser(BaseModel):
    type: Literal["GreetUser"] = "GreetUser"


class LookAtHuman(BaseModel):
    type: Literal["LookAtHuman"] = "LookAtHuman"
    captured_image: HttpUrl | None = None


class GenerateImage(BaseModel):
    type: Literal["GenerateImage"] = "GenerateImage"
    captured_image: HttpUrl
    generated_image: HttpUrl | None = None


class MirrorPhoto(BaseModel):
    """A shutter photo: the instant mirror frame first, the Flux render later."""

    action_uuid: str
    instant_image: HttpUrl
    hires_image: HttpUrl | None = None
    qr_code: HttpUrl | None = None
    status: Literal["processing", "ready", "failed"] = "processing"


class AppState(BaseModel):
    message_type: Literal["AppState"] = "AppState"
    transcript: Transcript | None = None
    animation: StaticAnimation | FillCircleAnimation | None = Field(
        discriminator="type", default=None
    )
    tool: AskHuman | LookAtHuman | GenerateImage | GreetUser | None = Field(
        discriminator="type", default=None
    )
    tracking_data: list[BoundingCircle]
    qr_code: HttpUrl | None = None
    countdown_started_at: float | None = None
    countdown_duration: float | None = None
    user_present: bool = False
    mirror_photo: MirrorPhoto | None = None
    # Shutter pressed and countdown/capture in progress; the button is disabled.
    shutter_busy: bool = False


class Signalling(BaseModel):
    message_type: Literal["Signalling"] = "Signalling"
    type: Literal["offer", "answer"]
    sdp: str


class AbortMessage(BaseModel):
    message_type: Literal["AbortMessage"] = "AbortMessage"


class ShutterMessage(BaseModel):
    """The kiosk's shutter button was pressed."""

    message_type: Literal["ShutterMessage"] = "ShutterMessage"


class BaseMessage(RootModel):
    root: AppState | Signalling | AbortMessage | ShutterMessage = Field(
        discriminator="message_type"
    )
