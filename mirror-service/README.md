# Mirror service

The magic mirror. It stylizes the live camera feed in near real time with
SD-Turbo img2img and TAESD, at 1 denoising step and 512×512, so people in front
of the kiosk see themselves transformed as they move.

| | |
|---|---|
| **In** | `camera_frame` (only the newest frame is kept), `mirror_style` (`ImageGeneration.prompt`), `user_state`, `tool_status` (`mirror_photo` renders) |
| **Out** | `stylized_frame` (JPEG `Frame`, with the same index and timestamp as the source frame) |
| **HTTP :7072** | `GET /frame.jpg` (latest stylized frame; `?fresh=1` waits for a new one), `GET /style`, `GET /health` |

## Styles

- A style someone asks for by voice (the agent's `set_mirror_style` tool) stays
  until they walk away, or for up to `user_style_hold_seconds`.
- Otherwise the mirror rotates through `idle_styles` every
  `idle_rotate_seconds`, to attract people walking by.
- The style is turned into an SD prompt as `"<style>, portrait of a person, high
  quality, detailed"`. The shutter's Flux render uses the same style, with
  Kontext's identity-preserving instruction.

## Performance (GB10, GPT-OSS 20B and FLUX.1 Kontext loaded)

| Backend | fps | Frame latency |
|---|---|---|
| TensorRT (`trt`, default) | ~30 (JPEG in/out included) | ~31 ms |
| `torch.compile` | ~24 | ~42 ms |
| eager | ~17 | ~60 ms |

- **Pause during hi-res renders (off in this booth):** `compose.yaml` sets
  `pause_during_render: false`, so the mirror stays live and photos can be taken
  back to back, at the cost of slower renders (~80 s). With it on (the code
  default), the mirror stops stylizing while a shutter photo's Flux render runs, and keeps
  re-sending its last frame, so the kiosk shows a still, stylized picture rather
  than the raw camera. A render takes about 43 s this way, against about 80 s
  with the mirror running. The `mirror_photo` STARTED and COMPLETED/FAILED
  statuses mark the start and end of the pause; `pause_timeout_seconds` resumes
  the mirror anyway if the end is never reported.
- **Fresh shutter frame:** the shutter fetches `/frame.jpg?fresh=1`, which
  stylizes one new frame even while paused, so a photo never shows the frozen
  frame.
- **TensorRT engines** are built on the first start (about 90 s, longer while
  Flux is busy) and cached in the `mirror_engines` volume. Later starts take
  about 15 s.
- **Fallback:** if the engines cannot be built, the service uses
  `torch.compile` instead.
- **Base image:** the service needs the NGC PyTorch image (cuDNN 9.27,
  TensorRT 11). The TRT-LLM image's cuDNN 9.10 is about 3× slower on GB10, and
  its TensorRT 10.11 cannot build engines on it. Background and measurements are
  in `scripts/mirror-spike/`.

## Configuration (`/config.yaml`)

`backend` (`trt` | `compile` | `eager`), `dtype` (`bf16` | `fp16`), `steps` (1–2),
`strength` (lower keeps the person, higher follows the style; default 0.5),
`size`, `max_fps`, `idle_styles`, `idle_rotate_seconds`, `user_style_hold_seconds`,
`pause_during_render`, `pause_timeout_seconds`, `hold_frame_interval`.

## Testing without the robot

`scripts/fake_camera.py` stands in for `camera-service`. It publishes frames from
an image or video file and serves `/capture`. Usage is in the script's
docstring.

## Licence

SD-Turbo is released under the Stability AI Community License; check its terms
before using it at a commercial event. TAESD is MIT-licensed.
