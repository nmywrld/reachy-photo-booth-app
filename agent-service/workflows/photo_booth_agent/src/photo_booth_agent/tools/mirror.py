# SPDX-License-Identifier: Apache-2.0
"""Magic mirror tools: change the live style, and take a photo by voice."""

import asyncio
import logging
import time

from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.common import TypedBaseModel
from nat.data_models.function import FunctionBaseConfig
from pydantic import Field
from workmesh.config import ConsumerConfig
from workmesh.messages import ImageGeneration, RemoteControlCommand, ToolStatus
from workmesh.service import Consumer, Producer

from photo_booth_agent.constant import SERVICE_NAME
from workmesh import (
    mirror_style_topic,
    remote_control_command_topic,
    tool_status_topic,
)

logger = logging.getLogger(SERVICE_NAME)

MIRROR_PHOTO_TOOL = "mirror_photo"
MAX_STYLE_CHARS = 200


class SetMirrorStyleConfig(FunctionBaseConfig, name="set_mirror_style"):
    pass


class SetMirrorStyleInput(TypedBaseModel, name="set_mirror_style"):
    action_uuid: str = Field(
        default="",
        description="""
The action UUID of the tool call.
This field will be set by the framework.
You don't need to set it, just leave it empty.
""",
    )
    style: str = Field(
        description="A short visual style for the live magic mirror, a few words "
        "an image model understands, e.g. 'pirate captain, oil painting', "
        "'Japanese anime illustration', 'astronaut, 3D animated movie character'. "
        "Describe the look, not the person. Use an empty string to go back to the "
        "rotating default styles.",
    )


@register_function(config_type=SetMirrorStyleConfig)
async def set_mirror_style(config: SetMirrorStyleConfig, builder: Builder):
    async def _arun(input: SetMirrorStyleInput) -> str:
        style = " ".join(input.style.split())[:MAX_STYLE_CHARS]
        async with Producer() as producer:
            await producer.publish(
                mirror_style_topic,
                ImageGeneration(
                    action_uuid=input.action_uuid,
                    timestamp=int(time.time() * 1000),
                    prompt=style,
                ),
            )
        if not style:
            return "The mirror is back to its rotating default styles."
        return f"The mirror now shows the user as: {style}. It updates within a second."

    yield FunctionInfo.create(
        single_fn=_arun,
        input_schema=SetMirrorStyleInput,
        description="Change the style of the live magic mirror the user sees "
        "themselves in. Use it whenever the user asks to look different.",
    )


class TakeMirrorPhotoConfig(FunctionBaseConfig, name="take_mirror_photo"):
    timeout: float = Field(
        default=30.0, description="Seconds to wait for the countdown and capture."
    )


class TakeMirrorPhotoInput(TypedBaseModel, name="take_mirror_photo"):
    action_uuid: str = Field(
        default="",
        description="""
The action UUID of the tool call.
This field will be set by the framework.
You don't need to set it, just leave it empty.
""",
    )


async def _wait_for_photo(since_ms: int, timeout: float) -> ToolStatus:
    """The next mirror_photo STARTED (photo taken) or FAILED (cancelled)."""
    # Own group: the default "Consumer" group is shared by other tool waiters,
    # and members of one group split a topic's messages between them.
    consumer = Consumer(ConsumerConfig(consumer_group="take_mirror_photo"))
    consumer.subscribe(tool_status_topic)  # pyright: ignore[reportArgumentType]
    try:
        async with asyncio.timeout(timeout):
            while True:
                result = await consumer.consume()
                if result is None:
                    continue
                message, _ = result
                if (
                    isinstance(message, ToolStatus)
                    and message.name == MIRROR_PHOTO_TOOL
                    and message.timestamp >= since_ms
                    and message.status
                    in (ToolStatus.TOOL_CALL_STARTED, ToolStatus.TOOL_CALL_FAILED)
                ):
                    return message
    finally:
        await consumer.close()


@register_function(config_type=TakeMirrorPhotoConfig)
async def take_mirror_photo(config: TakeMirrorPhotoConfig, builder: Builder):
    async def _arun(input: TakeMirrorPhotoInput) -> str:
        since_ms = int(time.time() * 1000)
        waiter = asyncio.create_task(_wait_for_photo(since_ms, config.timeout))
        await asyncio.sleep(0.5)  # let the consumer join before the photo starts
        # The same path as the kiosk's shutter button: countdown, flash, capture.
        async with Producer() as producer:
            await producer.publish(
                remote_control_command_topic,
                RemoteControlCommand(command="TakePicture"),
            )
        try:
            status = await waiter
        except TimeoutError:
            raise RuntimeError("The photo did not happen in time.") from None
        if status.status == ToolStatus.TOOL_CALL_FAILED:
            raise RuntimeError(
                "Photo cancelled: nobody was in front of the mirror. "
                "Ask the user to stand in front of the camera."
            )
        return (
            "Photo taken. It is on the screen with a QR code to download it. A "
            "high-resolution painted version appears on the same download page in "
            "about a minute."
        )

    yield FunctionInfo.create(
        single_fn=_arun,
        input_schema=TakeMirrorPhotoInput,
        description="Take a photo of the user in the current mirror style "
        "(3 second countdown). The user can also press the shutter button.",
    )
