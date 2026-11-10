# Connecting to the wireless Reachy

The right way to connect to the Reachy over Wi-Fi is a two-part pattern:

1. **Deploy the application onto the robot.** The app (`reachy_booth/`) runs on
   the robot itself and drives the motors and camera through the Reachy Mini
   SDK and daemon running locally on the robot. No network is involved at this
   hop.
2. **Use forwarding services on the host.** Host-side services never touch the
   robot directly. They connect to the app on the robot over the wireless
   network and pass commands to it / receive data from it.

```
Booth stack (Docker, host)                    reachy_booth app (on the robot)        Reachy Mini daemon
┌────────────────────────┤                      ┌─────────────────────┤                (on-robot, :8000)
│ robot-controller-service │ ─ WS /ws/motion ─► │ motion controller    │               │
│ (AnimationFrame from     │  (newest wins)     │ camera grabber       │ ─ ReachyMini  ►
│  Kafka `robot_frame`)    │ ◄─ HTTP ─────      │ (local SDK backend)  │   SDK, no     │
└────────────────────────┘  /camera/stream,   └─────────────────────┘    network
                            /camera/frame.jpg
```

Why this is the right way:

- **The control loop lives on the robot.** Rate limiting, unit conversion and
  motor safety all happen next to the motors. The wireless link only carries
  already-validated commands.
- **Wi-Fi lag degrades gracefully.** The host forwarder keeps only the newest
  frame ("newest frame wins"), so delays add lag but never queue stale motion.
- **The host holds no robot SDK or credentials.** Only the app on the robot
  talks to the daemon; host containers just know the app's URL.
- **Both ends self-heal.** The forwarder reconnects with backoff and a
  heartbeat; the app on the robot retries its local daemon connection forever,
  so an unattended booth recovers by itself.

## 1. Commands: forwarding to the robot

`robot-controller-service` (host) is the outbound forwarder:

- Subscribes to the `robot_frame` Kafka topic (animation frames composed by
  `animation-compositor-service`), filters by `robot_id` and timestamp, and
  forwards each `AnimationFrame` as JSON over **one WebSocket** to
  `ws://<robot>:8042/ws/motion`.
- Only the newest frame is kept and sent; while offline, frames are dropped.
- Reconnects with exponential backoff (1s → 10s cap); a 2s heartbeat ping
  detects dead links instead of silently stalling.
- On shutdown it POSTs `/zero` to return the robot to the zero pose.

Configuration (`booth_app` in `robot-controller-service/src/configuration.py`):

| Variable | Default | Purpose |
|---|---|---|
| `booth_app.url` | `http://reachy-mini.local:8042` | Base URL of the `reachy_booth` app on the robot. Use the robot's IP — mDNS names usually don't resolve in containers. |
| `booth_app.connect_timeout` | `5.0` | Seconds to open the WebSocket. |
| `booth_app.heartbeat` | `2.0` | WebSocket ping interval; a missed pong reopens the link. |
| `booth_app.max_reconnect_delay` | `10.0` | Upper bound of the reconnect backoff. |
| `booth_app.zero_on_stop` | `true` | Move to zero pose when the service stops. |

## 2. Data: receiving from the robot

The app on the robot serves camera data back to the host over HTTP
(`reachy_booth/reachy_booth/api.py`):

| Method | Path | Purpose |
|---|---|---|
| GET | `/camera/stream` | MJPEG live stream (size/fps/quality query-tunable). |
| GET | `/camera/frame.jpg` | Full-resolution still from the newest frame (max 2s old — a photo is never a stale still). |
| GET | `/health` | Liveness + camera/motion stats (always 200 while up). |
| GET | `/status` | Present pose in animation-frame units. |
| POST | `/reconnect` | Force-drop and retry the daemon connection. |
| POST | `/wake_up` \| `/sleep` \| `/zero` | Scripted moves (pause the motion stream). |

The camera itself is read locally through the SDK
(`reachy_mini.media.get_frame()`); only JPEG-encoded output crosses Wi-Fi.
`reachy_camera_probe.py` at the repo root probes the wireless camera directly
against the daemon's WebRTC/REST API for debugging.

## 3. The app on the robot

`reachy_booth/` runs on the robot (FastAPI + web UI). Its `RobotLink`
(`reachy_booth/reachy_booth/link.py`) owns the `ReachyMini` connection
(`connection_mode="localhost_only"`) and keeps it alive unattended:

- Connects at startup and retries every 3s if the daemon is unreachable.
- Marks the link dead after 5s without liveness and reconnects.
- `/health` always reports the current state; `/reconnect` forces a retry.

## External applications: the reachy-bridge

Apps that are **not** part of the booth stack (e.g. the Hermes sandbox) must
not connect to the robot or its daemon either. They go through a host-side
**bridge** that holds the robot address and enforces auth:

```
Application / Hermes sandbox
        │  HTTP + Bearer token         (port 8787)
        ▼
reachy-bridge  (FastAPI, runs on the host)
        │  HTTP, no auth, LAN only     (port 8000)
        ▼
Reachy daemon 1.9  (http://reachy-mini.local:8000)
```

Only the bridge holds the robot address and the bridge token. Applications get
a small, fixed set of actions, not arbitrary joint control.

### Network requirements

- The host running the bridge and the Reachy must be on the same network.
- The robot must be reachable at `reachy-mini.local:8000` (mDNS name) or by an
  IP address you set yourself.
- Robot traffic ignores `HTTP_PROXY`/`HTTPS_PROXY` (`trust_env=False`), so a
  host proxy will not interfere.
- Quick check from the host:

  ```bash
  curl http://reachy-mini.local:8000/api/daemon/status
  ```

  If this fails, fix DNS/mDNS or use the robot's IP before going further.

### Configure the bridge

Settings are read from environment variables with the `REACHY_` prefix, or from
a `.env` file in the bridge project root (see `src/reachy_bridge/config.py`).

| Variable | Default | Purpose |
|---|---|---|
| `REACHY_ROBOT_URL` | `http://reachy-mini.local:8000` | Robot daemon address. Must be `http(s)://host[:port]` with no credentials, query or fragment. |
| `REACHY_BIND` | `127.0.0.1` | Interface the bridge listens on. |
| `REACHY_PORT` | `8787` | Bridge port (1024-65535). |
| `REACHY_TOKEN_FILE` | `.secrets/bridge-token` | Bearer token file. Token must be 32+ characters, no whitespace. |
| `REACHY_DRY_RUN` | `false` | Simulate everything; never touches the robot or TTS. |
| `REACHY_TTS` | `espeak` | `espeak`, `openai` (OpenAI-compatible `/audio/speech`, e.g. Kokoro) or `none`. |
| `REACHY_TTS_BASE_URL` | `http://127.0.0.1:8880/v1` | Used when `REACHY_TTS=openai`. |

Example `.env` when the robot is addressed by IP:

```
REACHY_ROBOT_URL=http://192.168.1.50:8000
REACHY_TTS=openai
```

### Start and verify

```bash
reachy-bridge init            # create the bridge token (never overwrites one)
reachy-bridge preflight       # read robot status and API; no motion or audio
reachy-bridge serve           # start the bridge (add --dry-run to test safely)
reachy-bridge client status   # confirm the bridge answers
```

`preflight` exits 0 only if the robot is ready, its OpenAPI schema contains all
endpoints the bridge needs, and speech is configured (or TTS is `none`, or
dry-run is on). Required robot endpoints:

- `GET /api/daemon/status`, `/api/motors/status`, `/api/media/status`
- `POST /api/move/goto`, `/api/move/stop`
- `POST /api/media/play_sound`, `/api/media/stop_sound`, `/api/media/sounds/upload`
- `DELETE /api/media/sounds/{filename}`

If `missing_endpoints` is non-empty, the robot firmware is incompatible. The
bridge targets Reachy daemon 1.9.

### Call the bridge from your application

All routes except `/healthz` need `Authorization: Bearer <token>`, where the
token is the contents of `REACHY_TOKEN_FILE`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Liveness, no auth. |
| GET | `/v1/status` | Robot and speech readiness. |
| GET | `/v1/voice` | Voice-loop status. |
| POST | `/v1/events` | Queue an alert (returns `202`). |
| GET | `/v1/events/{event_id}` | Poll an event's state. |
| POST | `/v1/stop` | Stop motion and audio. |

Alert body (`extra` fields are rejected):

```json
{
  "event_id": "demo-1",
  "severity": "warning",
  "summary": "Checkout deployment has 1 of 3 replicas ready",
  "source": "my-app",
  "speak": true,
  "gesture": true
}
```

- `event_id`: 1-96 chars, `A-Za-z0-9_.:-`
- `severity`: `healthy`, `warning`, `critical`, `recovering` or `unknown`
- `summary`: 1-600 characters, no control characters

Example:

```bash
TOKEN=$(cat .secrets/bridge-token)
curl -X POST http://127.0.0.1:8787/v1/events \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"event_id":"demo-1","severity":"warning","summary":"Replica count is low"}'

curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8787/v1/events/demo-1
```

Event states: `queued`, `running`, `completed`, `failed`, `cancelled`, `expired`.
Events older than `REACHY_EVENT_MAX_AGE` seconds (default 120) expire, and the
queue is bounded (`REACHY_QUEUE_SIZE`, default 8). Examples are in `examples/`.

### Connecting from the Hermes (OpenShell) sandbox

The sandbox cannot reach the host by default. A narrow network policy is needed
in `deploy/reachy-bridge-policy.yaml`:

- host `host.openshell.internal`, port `8787`
- `allowed_ips` pinned to the host bridge address (currently `172.18.0.1/32`)
- allowed requests only: `GET /v1/status`, `GET /v1/events/*`,
  `POST /v1/events`, `POST /v1/stop`
- allowed binary: `/usr/bin/python3.13`

If the bridge's address changes, regenerate and reapply the policy:

```bash
reachy-bridge policy --allowed-ip <bridge-ip-as-seen-from-openshell>
reachy-bridge policy --allowed-ip <ip> --base exported-base.yaml   # merge into an existing policy
```

The Hermes plugin (`hermes-plugin/`) uses this path. It registers the tools
`reachy_report`, `reachy_stop` and `reachy_event_status`, and the sandbox only
ever calls the bridge, never the robot.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Cannot read robot status; check host DNS, robot URL and daemon` | Robot off, not on the same network, `.local` name not resolving, or wrong `REACHY_ROBOT_URL`. |
| `Cannot read robot OpenAPI schema` | Daemon reachable but not serving `/openapi.json`; check the daemon version. |
| `api_compatible: false` | Firmware is missing endpoints listed in `missing_endpoints`. |
| `401 Invalid bridge credential` | Missing or wrong Bearer token. |
| `Bridge token must have at least 32 characters` | Re-run `reachy-bridge init` or use a longer token. |
| Sandbox requests blocked | Bridge address changed; update `allowed_ips` and reapply the policy. |
| Robot unready, nothing moves | Bridge refuses to send mutations to an unready robot. Fix `preflight` first. |

Use `--dry-run` or `REACHY_DRY_RUN=true` to test applications against the bridge
without a robot.

Booth-specific symptom — the stack logs
`Reachy link down (...); retrying. Is the reachy_booth app running at <url>?`:
the `reachy_booth` app is not running on the robot, or `booth_app.url` points
at the wrong host/port.
