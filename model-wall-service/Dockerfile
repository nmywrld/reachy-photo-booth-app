# SPDX-License-Identifier: Apache-2.0

FROM ghcr.io/astral-sh/uv:0.8.24-python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=./workmesh,target=/app/workmesh \
    uv sync --frozen --no-install-project --package model-wall --no-editable

FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app/src

ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY ./model-wall-service /app

# Runs as root: mapping GPU processes to containers reads /proc/<pid>/root.
ENTRYPOINT [ "bash", "-c" ]
CMD [ "python main.py" ]
