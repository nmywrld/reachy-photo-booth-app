# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import signal
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from activity import MODELS, ActivityTracker
from configuration import ModelWallConfig
from fastapi import FastAPI
from fastapi.responses import FileResponse
from gpu import GpuSampler
from workmesh.config import load_config
from workmesh.messages import (
    ClipData,
    HumanSpeechRequest,
    ToolStatus,
    UserDetection,
    UserUtterance,
    UserUtteranceStatus,
)
from workmesh.service import Service, subscribe
from workmesh.service_executor import ServiceExecutor

from workmesh import (
    clip_data_topic,
    human_speech_request_topic,
    tool_status_topic,
    user_detection_topic,
    user_utterance_topic,
)

INDEX_HTML = Path(__file__).parent / "static" / "index.html"
IMAGE_TOOL = "generate_image"


class ModelWallService(Service):
    def __init__(self, config: ModelWallConfig, tracker: ActivityTracker) -> None:
        self.tracker = tracker
        super().__init__(config)

    @subscribe(user_utterance_topic)
    async def on_utterance(self, message: UserUtterance) -> None:
        if message.status == UserUtteranceStatus.USER_UTTERANCE_FINISHED:
            self.tracker.stop("stt", message.action_uuid)
            self.tracker.pulse("stt", 0.5)
        else:
            self.tracker.start("stt", message.action_uuid, ttl=30)

    @subscribe(human_speech_request_topic)
    async def on_speech_request(self, message: HumanSpeechRequest) -> None:
        self.tracker.start("tts", message.action_uuid, ttl=20)

    @subscribe(clip_data_topic)
    async def on_clip(self, message: ClipData) -> None:
        if message.HasField("audio"):
            self.tracker.stop("tts", message.action_uuid)
            self.tracker.pulse("tts", 0.5)

    @subscribe(tool_status_topic)
    async def on_tool(self, message: ToolStatus) -> None:
        if message.name != IMAGE_TOOL:
            return
        if message.status == ToolStatus.TOOL_CALL_STARTED:
            self.tracker.start("flux", message.action_uuid, ttl=180)
        elif message.status in (
            ToolStatus.TOOL_CALL_COMPLETED,
            ToolStatus.TOOL_CALL_FAILED,
        ):
            self.tracker.stop("flux", message.action_uuid)

    @subscribe(user_detection_topic)
    async def on_detection(self, _message: UserDetection) -> None:
        self.tracker.pulse("vision", 1.0)


class LlmReportProtocol(asyncio.DatagramProtocol):
    def __init__(self, tracker: ActivityTracker) -> None:
        self.tracker = tracker

    def datagram_received(self, data: bytes, addr) -> None:
        self.tracker.handle_llm_datagram(data)


async def sample_gpu(app: FastAPI, sampler: GpuSampler, interval: float) -> None:
    while True:
        app.state.gpu = await asyncio.to_thread(sampler.sample)
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config(ModelWallConfig)
    tracker = ActivityTracker()
    sampler = GpuSampler()
    app.state.tracker = tracker
    app.state.gpu = await asyncio.to_thread(sampler.sample)

    transport, _ = await asyncio.get_running_loop().create_datagram_endpoint(
        lambda: LlmReportProtocol(tracker),
        local_addr=("0.0.0.0", config.udp_port),
    )
    executor = ServiceExecutor([ModelWallService(config, tracker)])

    async def run_service() -> None:
        try:
            await executor.run(handle_sigint=False)
        except Exception:
            os.kill(os.getpid(), signal.SIGINT)

    service_task = asyncio.create_task(run_service())
    sampler_task = asyncio.create_task(
        sample_gpu(app, sampler, config.sample_interval_seconds)
    )
    yield
    sampler_task.cancel()
    transport.close()
    await executor.cleanup_async()
    await service_task


app = FastAPI(lifespan=lifespan)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(INDEX_HTML, headers={"Cache-Control": "no-cache"})


@app.get("/api/stats")
async def stats() -> dict:
    gpu = app.state.gpu
    tracker: ActivityTracker = app.state.tracker
    memory_by_container = gpu["container_memory_bytes"]
    return {
        "gpu": {key: v for key, v in gpu.items() if key != "container_memory_bytes"},
        "tokens": tracker.token_stats(),
        "models": [
            {
                "id": model.id,
                "name": model.name,
                "role": model.role,
                "active": tracker.is_active(model.id),
                "memory_bytes": memory_by_container.get(model.container),
            }
            for model in MODELS
        ],
    }


if __name__ == "__main__":
    config = load_config(ModelWallConfig)
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
        workers=1,
    )
