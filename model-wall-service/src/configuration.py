# SPDX-License-Identifier: Apache-2.0

from pydantic import Field
from workmesh.config import BaseConfig


class ModelWallConfig(BaseConfig):
    host: str = Field(default="0.0.0.0", description="Web server bind address.")
    port: int = Field(default=9100, description="Web server port.")
    udp_port: int = Field(default=9101, description="Port for agent LLM reports.")
    sample_interval_seconds: float = Field(default=1.0, gt=0)
