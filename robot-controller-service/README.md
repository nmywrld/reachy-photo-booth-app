# Robot Controller Service

## Overview

The Robot Controller Service moves the wireless Reachy Mini. It subscribes to the
`robot_frame` topic (animation frames from the animation compositor) and forwards
the newest frame over one websocket to the **reachy_booth** app running on the
robot.

The reachy_booth app ([`reachy_booth/`](../reachy_booth/)) drives the motors with
the Reachy Mini Python SDK on the robot itself: a 50 Hz control loop, rate
limiting and unit conversion all happen there. This service has no SDK, USB or
audio dependency. Setup and publishing of the app:
[docs/wireless-reachy-booth-app.md](../docs/wireless-reachy-booth-app.md).

```
animation-compositor ──robot_frame──► robot-controller ──WS /ws/motion──► reachy_booth (robot)
```

Behaviour on a flaky link:

- Only the newest frame is sent; frames that arrive while the link is busy or
  down replace each other instead of queueing.
- A websocket heartbeat (every `heartbeat` seconds) detects a dead link; the
  service reconnects with backoff (up to `max_reconnect_delay`) and logs
  `Reachy link down (...)` once per cause and `Connected to the reachy_booth app`
  when it is back.
- While no frame arrives, the robot holds its last pose.
- On shutdown the robot moves to the zero pose (`zero_on_stop`).

## Running the Service

### Prerequisites

| Service | Description |
|---------|-------------|
| `redpanda` | Message broker for Kafka communication |
| `agent` | LLM-powered agent service |
| reachy_booth app | Running on the robot (port 8042) |

The container is healthy once `http://<robot-ip>:8042/health` answers. Services
that depend on it wait until then, so start the app on the robot first.

### Starting the Service

```bash
uv run robot-controller-service/src/main.py
```

## Configuration

Set in [compose.yaml](./compose.yaml):

```yaml
configs:
  config_robot_controller:
    content: |
      booth_app:
        url: http://192.168.0.25:8042   # the robot's IP; mDNS names rarely resolve in containers
        # heartbeat: 2.0                # websocket ping interval (s)
        # max_reconnect_delay: 10.0     # reconnect backoff cap (s)
        # zero_on_stop: true            # zero pose when the service stops
```

Use the same IP in the `healthcheck` of [compose.yaml](./compose.yaml).

Motion limits (maximum joint speeds) live in the app:
[`reachy_booth/reachy_booth/motion.py`](../reachy_booth/reachy_booth/motion.py)
(`DEFAULT_MAX_SPEED`). Motor PID values belong to the robot's own daemon
configuration, not to this service.

### Simulation

Run a simulated daemon and the app on the same machine, then point `booth_app.url`
at it:

```bash
reachy-mini-daemon --sim                     # terminal 1
cd reachy_booth && python -m reachy_booth.main   # terminal 2 (serves port 8042)
```

The simulator has no camera, so only motion works.

## Development Scripts

`extract_positions.py` and `play_positions.py` talk to the robot with the Reachy
Mini SDK, which is no longer a dependency of this service. Run them with it added:

```bash
# Extract "Message position" entries from controller logs (log_level: DEBUG)
uv run robot-controller-service/scripts/extract_positions.py logs_data.csv

# Replay positions on the robot at 30 FPS
uv run --with reachy-mini robot-controller-service/scripts/play_positions.py positions.csv
```

`speaker_setup.sh` sets the volume of a USB-connected ReSpeaker; it does not
apply to the wireless robot, whose audio is configured from its dashboard.
