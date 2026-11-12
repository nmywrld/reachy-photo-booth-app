# Running the photo booth with a wireless Reachy Mini

The photo booth talks to a wireless Reachy Mini through **reachy_booth**, a Reachy
Mini Python app that runs on the robot. This guide covers what it does, how to
publish it to Hugging Face, how to install and run it on the robot, and how to
point the booth's containers at it.

## How it fits together

```
GB10 host (Docker)                                Reachy Mini (on-board CM4)
──────────────────                                ──────────────────────────────────
animation-compositor ──robot_frame──┐             reachy_booth app (port 8042)
                                    ▼               ReachyMini() on localhost
                         robot-controller ──WS /ws/motion──► 50 Hz set_target() loop
                                                    │
camera ◄──── GET /camera/stream (MJPEG 640x360) ────┤  media.get_frame() (local camera)
       ◄──── GET /camera/frame.jpg (1280x720) ──────┘
  │
  └─camera_frame──► tracker, ui-server
```

The SDK runs on the robot, so the motion control loop and camera capture never
cross Wi-Fi. Only small JSON motion frames and JPEGs travel over the network,
on plain HTTP and websocket (TCP). A weak link causes lag; it no longer breaks
the session:

| Before | Now |
|---|---|
| SDK websocket from the host; dead after 1 s without data, never reconnected | Websocket to the app with heartbeat and automatic reconnect; newest frame wins |
| Camera over WebRTC (ICE/DTLS) from the host; sessions failed on packet loss | MJPEG over HTTP, reconnects with backoff; photos fetched as separate full-resolution stills |

Nothing else in the booth changed: the `robot_frame` and `camera_frame` topics
and the camera's `GET :7071/capture` endpoint behave as before.

## Files

| Path | What it is |
|---|---|
| [`reachy_booth/`](../reachy_booth/) | The robot app, scaffolded with `reachy-mini-app-assistant`. Code in `reachy_booth/reachy_booth/` (`main.py`, `api.py`, `motion.py`, `camera.py`), status page in `static/`, unit tests in `tests/`. |
| [`robot-controller-service/`](../robot-controller-service/) | Forwards `robot_frame` to the app's `/ws/motion`. No SDK dependency any more. |
| [`camera-service/src/reachy_booth_camera.py`](../camera-service/src/reachy_booth_camera.py) | Reads the app's MJPEG stream and stills for `camera_serial_or_url: reachy://<ip>`. |

## 1. Prerequisites

- The robot is on and reachable: `curl http://192.168.0.25:8000/api/daemon/status`.
  Replace `192.168.0.25` with your robot's IP everywhere in this guide
  (`scripts/reachy-ip.sh` prints it).
- A Python environment with `reachy-mini` on your workstation, for the app assistant.
  The repository's `.reachy-env` has it, but that venv was moved from `reachy-env/`,
  so its console scripts (`reachy-mini-app-assistant`, `hf`, ...) point to a path
  that no longer exists. Either recreate it, or call the assistant through Python:

  ```bash
  alias reachy-mini-app-assistant='.reachy-env/bin/python -c "import sys; from reachy_mini.apps.app import main; sys.argv[0]=\"reachy-mini-app-assistant\"; main()"'
  ```

- A Hugging Face account and a **write** access token
  (https://huggingface.co/settings/tokens).

## 2. Check the app before publishing

From the repository root:

```bash
reachy-mini-app-assistant check reachy_booth
```

Optional, the motion unit tests (needs `pytest`, `opencv-python` and `reachy-mini`):

```bash
cd reachy_booth && python -m pytest tests
```

## 3. Publish it to Hugging Face

Publishing creates a Hugging Face Space that holds the app's code (a git repo). The
robot installs apps from Spaces.

```bash
pip install --upgrade huggingface_hub
hf auth login --token $HF_TOKEN --add-to-git-credential   # token with write access

reachy-mini-app-assistant publish reachy_booth "Initial version" --private
```

The Space appears at `https://huggingface.co/spaces/<your-username>/reachy_booth`.
`--private` keeps it to your account; use `--public` to share it.

To publish changes later, run the same command with a new message:

```bash
reachy-mini-app-assistant publish reachy_booth "Describe the change" --private
```

## 4. Install and run it on the robot

1. Open the robot dashboard: `http://192.168.0.25:8000`.
2. For a **private** Space, sign in to Hugging Face from the dashboard first, so the
   robot can see your private apps.
3. Under **Install from Hugging Face**, find `reachy_booth` and click **Install**.
4. Under **Applications**, click **Run** on `reachy_booth`. The robot runs one app at a
   time, so this stops the testbench (which also uses port 8042).
5. Check it is up:

   ```bash
   curl http://192.168.0.25:8042/health
   ```

   `camera_ok: true` and `camera.fps` around 30 mean the camera works. The ⚙️ icon
   on the running app (or `http://192.168.0.25:8042`) opens a status page with
   wake/sleep/zero buttons and an optional camera preview.

The daemon's REST API can do the same without the dashboard, e.g. after a reboot:

```bash
curl -X POST http://192.168.0.25:8000/api/apps/start-app/reachy_booth
curl http://192.168.0.25:8000/api/apps/current-app-status
curl -X POST http://192.168.0.25:8000/api/apps/stop-current-app
```

After publishing an update, the dashboard offers to update the installed app; stop
and run it again to load the new version.

### Quicker loop while developing: run it by hand on the robot

Instead of publishing every change, copy the app to the robot and run it from the
robot's app environment (`/venvs/apps_venv`), the same way you ran the testbench:

```bash
# from the repository root on your workstation
scp -r reachy_booth <user>@192.168.0.25:~/

# on the robot (ssh <user>@192.168.0.25)
curl -X POST http://localhost:8000/api/apps/stop-current-app   # frees port 8042
/venvs/apps_venv/bin/pip install -e ~/reachy_booth
cd ~/reachy_booth && /venvs/apps_venv/bin/python -m reachy_booth.main
```

Stop it with Ctrl+C. An editable install (`-e`) also shows up in the dashboard's
installed applications.

## 5. Point the booth at the robot

The robot's IP lives in one place, `REACHY_HOST` in the repository's `.env`. Both
[`camera-service/compose.yaml`](../camera-service/compose.yaml) and
[`robot-controller-service/compose.yaml`](../robot-controller-service/compose.yaml)
read it. Containers cannot resolve mDNS names such as `reachy-mini.local`, so it
holds the IP itself.

The robot gets a new IP whenever it joins another network or the router hands out a
different lease. To follow it:

```bash
scripts/reachy-ip.sh              # finds reachy-mini.local by mDNS, updates .env,
                                  # recreates camera + robot-controller if running
scripts/reachy-ip.sh 10.0.0.42    # or give the IP yourself
```

To stop the IP changing on a network you control, reserve it for the robot in the
router's DHCP settings (by the robot's MAC address). A phone hotspot usually can't
do this, so run the script after switching to one.

Rebuild the two changed images and start the stack:

```bash
docker compose build camera robot-controller
docker compose up -d
```

Start the app on the robot first: `robot-controller` only reports healthy once
`/health` answers, and the services that depend on it wait for that.

## 6. Verify

```bash
docker compose logs robot-controller | grep -E "Connected to the reachy_booth app|link down"
docker compose logs camera | grep -E "Reachy video"
curl -s http://192.168.0.25:8042/health | python3 -m json.tool
```

- `robot-controller` logs `Connected to the reachy_booth app`.
- `camera` logs `Reachy video streaming from http://192.168.0.25:8042`.
- After you say "hey Reachy, wake up", `/health` shows `motion.streaming: true` and
  a growing `frames_received`, and the robot moves.

## Tuning for your Wi-Fi

On the current link (about 0.46 MB/s measured), the defaults keep the live stream
around 0.3 MB/s:

| Setting (camera-service compose) | Default | Effect |
|---|---|---|
| `streaming_resolution` | 640x360 | Live view, tracking and UI preview size |
| `fps` | 12 | Live stream rate; also used by the photo freshness check |
| `reachy_stream_quality` | 65 | JPEG quality of the live stream |
| `capture_resolution` | 1280x720 | Photo size; fetched separately at full resolution |

With a better connection (Ethernet on the host, robot close to the access point),
raise `fps` to 15-25 and `streaming_resolution` to 1280x720.

Motion speed limits are in [`motion.py`](../reachy_booth/reachy_booth/motion.py)
(`DEFAULT_MAX_SPEED`, per joint per second). They only cap spikes and catch-up moves
after a link outage.

## Troubleshooting

| Symptom | Check |
|---|---|
| `robot-controller` stays unhealthy | `curl http://192.168.0.25:8042/health`. If it fails, the app is not running: start it from the dashboard. |
| UI shows black, camera logs `Reachy video unavailable ... Is the reachy_booth app running` | Same as above. If `/health` works but `camera_ok` is false, the robot's camera is busy or the daemon has no media: restart the app. |
| `/health` works but the robot does not move | `motion.clients` should be 1 (the controller). If `streaming` is false after a wake word, check the controller logs for `link down`. If the motors are off, `POST /wake_up` (or the dashboard) turns the robot on. |
| Robot moves, then pauses for a second at a time | Wi-Fi stalls: the robot holds its pose until the next frame. Improve the link (see Tuning). |
| `/health` shows `daemon.connected: false` | The app is up but cannot reach the robot's daemon (`daemon.error` says why). It retries every 3 s by itself; `POST /reconnect` (or the status page button) retries immediately. Check `curl http://localhost:8000/api/daemon/status` on the robot. |
| Status page says "DAEMON OFF" with checks failing | That is the **testbench** page, not this app: the testbench connects once at startup and stays off until its `/api/reconnect`. Stop it and run `reachy_booth`, which reconnects on its own. |
| Port 8042 already in use on the robot | Another app (e.g. the testbench) is running: stop it first. |

## App API reference

| Endpoint | Purpose |
|---|---|
| `WS /ws/motion` | Animation frames as JSON: `body_angle`, `r_antenna_angle`, `l_antenna_angle` (degrees), `head_position_x/y/z` (cm), `head_rotation: {roll, pitch, yaw}` (degrees). Missing fields are 0. Newest frame wins. |
| `GET /camera/stream` | MJPEG. Query: `width`, `height`, `fps`, `quality`. |
| `GET /camera/frame.jpg` | Full-resolution still from the newest frame, never older than 2 s (503 otherwise). Query: `quality`. |
| `POST /wake_up`, `/sleep`, `/zero` | Scripted moves. Motion streaming pauses during the move and resumes from the new pose; a second move while one runs returns 409. |
| `GET /health` | Always 200 while the app runs: daemon connection state, camera frame age and rate, motion stats. |
| `POST /reconnect` | Drop and re-make the daemon connection now. |
| `GET /status` | Present pose, in animation-frame units. |
