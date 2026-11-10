---
title: Reachy Booth
emoji: 📸
colorFrom: red
colorTo: blue
sdk: static
pinned: false
short_description: On-robot motion and camera bridge for the Reachy photo booth
tags:
 - reachy_mini
 - reachy_mini_python_app
---

# Reachy Booth

The on-robot half of the Reachy photo booth. It runs on the wireless Reachy Mini,
uses the Python SDK on the robot's own localhost, and gives the photo booth's host
services a small API on port 8042:

| Endpoint | Purpose |
|---|---|
| `WS /ws/motion` | Animation frames (JSON, degrees and cm). The newest frame wins; a 50 Hz control loop on the robot applies it with rate limiting. |
| `GET /camera/stream` | MJPEG live stream, by default 640×360 at 12 fps (tunable with `width`, `height`, `fps`, `quality`). |
| `GET /camera/frame.jpg` | Full-resolution still from the newest frame (never older than 2 s). |
| `POST /wake_up`, `/sleep`, `/zero` | Scripted moves. |
| `GET /health`, `GET /status` | Liveness, camera and motion stats, present pose. |

Motion control and camera capture stay on the robot, so a flaky Wi-Fi link adds
lag instead of breaking the session.

Setup, publishing and running: see `docs/wireless-reachy-booth-app.md` in the
photo booth repository.
