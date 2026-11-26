# Magic Mirror conversion: models and plan

## Context
The booth today is queue-based: the LLM talks with one person, a single photo is taken, and FLUX.1 Kontext renders it in 10–30 s. The goal is a "magic mirror": the kiosk shows the live camera feed stylized in near real time, so passers-by see themselves transformed instantly with no queue. A shutter button on the UI still takes a photo.

Decisions you made:
- **Voice:** Reachy keeps light voice use. Spoken requests like "make me a pirate" change the mirror's style.
- **Shutter:** hands over both the instant mirror frame and a hi-res Flux render.
- **Look:** prompt-driven diffusion.
- **Robot:** detects presence only, with no head tracking.

## Model inventory

| Model | Today | Mirror | Why |
|---|---|---|---|
| **SD-Turbo img2img via StreamDiffusion + TensorRT** | — | **ADD** (new `mirror` service) | The real-time stylizer: 1–2 denoising steps per frame at 512 px, with any style set by a text prompt. |
| **TAESD (tiny VAE)** | — | **ADD** | Replaces the full VAE encode/decode, which would otherwise dominate the per-frame cost. Same family as SD-Turbo. |
| **Light person detector** (e.g. torchvision SSDLite-MobileNetV3, COCO person, BSD license) | — | **ADD**, replacing Detectron2 | Presence and a bounding box are still needed to wake and reset sessions and to keep `PhotoGate` working. Pose keypoints and head tracking are not. |
| GPT-OSS 20B (TensorRT-LLM) | Runs the whole session | **KEEP, smaller** | Turns speech into style prompts, says the robot's lines, and enforces the safety rules. Cut its KV-cache reservation so the mirror fits. |
| Parakeet + VAD + Sortformer (Riva) | Speech to text | **KEEP** | Still needed for spoken style requests. |
| Kokoro-82M | Text to speech | **KEEP** | Greetings, countdown, quips. |
| FLUX.1 Kontext NIM | Main photo | **KEEP**, final print only | Hi-res render of the raw photo in the chosen style, delivered after the instant frame. |
| Detectron2 Keypoint R-CNN | Detection + pose | **REMOVE** | Replaced by the light detector. |
| ByteTrack (CPU) | Keeps a person's ID across frames | **REMOVE** | Only needed for head tracking, which is dropped. |

Net: 3 added (stylizer, tiny VAE, light detector), 2 removed (Detectron2, ByteTrack), 4 kept.

## Design

1. **Spike first, on the Spark.** Benchmark StreamDiffusion with SD-Turbo, TAESD and TensorRT at 512×512 and 1 step, with Flux and the LLM loaded. Go/no-go: at least 12 fps, latency under 150 ms, and the memory fits. **No GB10 benchmark exists yet; fps figures are estimates.**
2. **New `mirror-service`** (GPU, same layout as `metrics-service`, using a workmesh `Service`):
   - **Input:** subscribes to `camera_frame`, keeps only the newest frame and drops stale ones (same pattern as `tracker-service/src/main.py:134-146`).
   - **Output:** center-crops to 512×512, stylizes, and publishes on a new `stylized_frame` topic. It reuses the `Frame` proto, which needs no proto change, and stays JPEG so it fits the 1 MB Kafka limit.
   - **Style input:** listens for a style message. It reuses the `ImageGeneration` message, which already exists but is unused (`messages.proto:243`, its `prompt` field), on a new `mirror_style` topic.
   - **Debug view:** serves `GET /frame.jpg` for the latest stylized frame.
3. **Camera feed:** raise the live stream in `camera-service/compose.yaml` from 640×360 at 12 fps to around 15–20 fps, aiming for a square-ish crop. Keep 1280×720 stills for the Flux input. Check that the robot's Wi-Fi link can sustain the higher rate.
4. **Display:** in `ui-server-service/src/main.py`, the kiosk WebRTC track takes `stylized_frame` instead of `camera_frame`, falling back to the raw feed if the mirror is down. Set the `StreamTrack` size to the stylized frame size rather than upscaling to a fixed 1080p (`session.py:25`). `VideoFeed.tsx` is unchanged. The mirror view is always visible while someone is present, not only in certain states (`App.tsx:98-101`).
5. **Voice-driven style:** add an agent tool `set_mirror_style(prompt)` that publishes to `mirror_style`. Rework `photobooth.yml` so the LLM turns requests into short SD-Turbo prompts, keeping the existing safety rules (`photobooth.yml:196-239`). The `ask_human`, `look_at_human` and `generate_image` flow is no longer the only route to a photo. Keep a default idle style that rotates on a timer.
6. **Shutter button** (the UI has no touch input today):
   - **Frontend:** add a button that sends a new `ShutterMessage` over `/ws` (alongside `AbortMessage` in `ui-server-service/src/messages.py:82-93`).
   - **ui-server:** publishes `RemoteControlCommand("TakePicture")`.
   - **interaction-manager:** already runs the countdown, flash and animation for this (`photo_booth_bot.py:789-818, 879-895`). Then add the missing capture step:
     - a. Grab the current stylized frame from the mirror and the raw still from `camera:7071/capture`.
     - b. Upload the instant frame with the Dell overlay and show its QR code right away. Reuse the MinIO, QR and frame helpers in `agent-service/.../tools/image_generation.py:145-270, 495-595`, moved into a shared module.
     - c. Queue a Flux render of the raw still using the current style prompt. When it finishes, update the same download page so the hi-res version appears there.
   - The download page's presigned URL lasts only 5 minutes today. Lengthen that window, or make the page poll for the hi-res file.
7. **Presence detector:** implement the existing detector interface (`tracker-service/src/models/detector/base.py`, `create_detector`) with SSDLite and set it as the default. Disable head-tracking states and keep `PhotoGate` (`workmesh/photo_gate.py`).
8. **Memory budget:**
   - Cap the LLM's KV cache through an `extra_llm_api_options` file on `trtllm-serve` (`docker-compose.yaml:391`). Confirm the exact option name for this image during the spike.
   - Start the mirror after the LLM is healthy, the same pattern Riva uses (`docker-compose.yaml:68`).
   - Add a `mirror` block to the model wall (`model-wall-service/src/activity.py` `MODELS`), with activity driven by `stylized_frame`, and remove the Detectron2 block.

## Risks
- **Flux contention:** a Flux render competes with the mirror for GPU compute, so the live feed will slow during renders. Consider fewer Flux steps for the print.
- **Image quality:** SD-Turbo at 1–2 steps flickers between frames and people may not look like themselves. That is accepted for "prompt-driven diffusion", but tune the img2img strength.
- **Licenses:** SD-Turbo and TAESD are under the Stability AI Community License, so check the terms for your event. FLUX.1 Kontext-dev is already non-commercial.
- **Latency path:** robot Wi-Fi, then Kafka JPEG, then aiortc software encoding, all on the CPU. If total latency is too high, the mirror should read the robot's MJPEG stream directly.

## Verification
- **Spike script:** fps, latency and memory on the Spark, with and without a concurrent Flux render.
- **Unit tests:** stale-frame dropping, style switching, the shutter message being parsed and published, and the detector interface. Extend `tests/src/` where the existing patterns fit.
- **End to end on the booth:**
  1. Walk up: the mirror wakes and shows the styled feed.
  2. Say a style: the feed changes within about 1 s.
  3. Press the shutter: countdown, instant photo and QR code within 2 s, then the hi-res image appears on the QR page.
- **Model wall:** shows the mirror block active, with memory per container.
