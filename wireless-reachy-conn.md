# Connecting applications to the wireless Reachy

This project does not use the Reachy SDK, WebRTC or robot discovery. Applications
never talk to the robot directly. They talk to a **host-side bridge**, and the
bridge talks to the robot's HTTP daemon over the local network (Wi-Fi or LAN).

```
Application / Hermes sandbox
        │  HTTP + Bearer token         (port 8787)
        ▼
reachy-bridge  (FastAPI, runs on the host)       src/reachy_bridge/service.py
        │  HTTP, no auth, LAN only     (port 8000)
        ▼
Reachy daemon 1.9  (http://reachy-mini.local:8000)   src/reachy_bridge/robot.py
```

Only the bridge holds the robot address and the bridge token. Applications get
a small, fixed set of actions, not arbitrary joint control.

## 1. Network requirements

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

## 2. Configure the bridge

Settings are read from environment variables with the `REACHY_` prefix, or from
a `.env` file in the project root (see `src/reachy_bridge/config.py`).

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

## 3. Start and verify

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

## 4. Call the bridge from your application

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

## 5. Connecting from the Hermes (OpenShell) sandbox

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

## 6. Troubleshooting

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
