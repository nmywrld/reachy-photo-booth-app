#!/usr/bin/env bash
# Run a spike script inside a GPU image.
# Usage: scripts/mirror-spike/run.sh [--script profile_parts.py] --backend trt --input /work/person.png
#   IMAGE=mirror-spike:latest (default; build with: docker build -t mirror-spike scripts/mirror-spike)
#   IMAGE=nvcr.io/nvidia/tensorrt-llm/release:spark-single-gpu-dev  (older cuDNN 9.10 / TRT 10.11)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="${OUT_DIR:-$here/out}"
image="${IMAGE:-mirror-spike:latest}"
script=bench.py
if [[ "${1:-}" == "--script" ]]; then script="$2"; shift 2; fi
mkdir -p "$out"
extra=()
# The TRT-LLM image does not put TensorRT on the library path by itself.
[[ "$image" == *tensorrt-llm* ]] && extra+=(-e LD_LIBRARY_PATH=/usr/local/tensorrt/targets/aarch64-linux-gnu/lib)
exec docker run --rm --gpus all --ipc=host --network host -w /work "${extra[@]}" \
  -e HF_HUB_DISABLE_TELEMETRY=1 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -v "${TORCH_CACHE:-$HOME/.cache/mirror-spike-torch}:/root/.cache/torch_compile" \
  -e TORCHINDUCTOR_CACHE_DIR=/root/.cache/torch_compile \
  -v "$here:/work:ro" -v "$out:/out" \
  --entrypoint python3 "$image" "/work/$script" "$@"
