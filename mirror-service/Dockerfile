# SPDX-License-Identifier: Apache-2.0
# NGC PyTorch ships torch, cuDNN and TensorRT built for GB10 (sm_121). The older
# TRT-LLM image's cuDNN 9.10 ran convolutions ~3x slower and its TensorRT 10.11
# could not build engines on this GPU (see scripts/mirror-spike).
FROM nvcr.io/nvidia/pytorch:26.10-py3

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HF_HUB_DISABLE_TELEMETRY=1

# NGC's torchao is newer than diffusers 0.35 expects and breaks its import.
RUN pip install diffusers==0.35.1 transformers==4.55.0 accelerate==1.10.1 aiohttp \
 && pip uninstall -y torchao

# The base image's PyYAML is Debian-installed (no RECORD), so pip cannot upgrade it in place.
COPY ./workmesh /tmp/workmesh
RUN pip install --ignore-installed pyyaml /tmp/workmesh && rm -rf /tmp/workmesh

COPY ./mirror-service/src /app/src
WORKDIR /app/src

ENTRYPOINT [ "python", "-u" ]
CMD [ "main.py" ]
