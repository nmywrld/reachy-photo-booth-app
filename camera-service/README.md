# Camera Service

The Camera Service captures images or video frames from either a physical camera device or a virtual camera (such as the simulator's Unity camera) and provides them to other components of the robot system, such as vision, interaction, or web ui modules.

## Running the Service

### Prerequisites

Start the required infrastructure services:

| Service | Description |
|---------|-------------|
| `redpanda` | Message broker for Kafka communication |

These can be started via Docker Compose from the repository root.

### Starting the Service

```bash
uv run camera-service/src/main.py
```

## Overview

The Camera Service abstracts camera hardware and network video sources, ensuring a consistent interface for acquiring real-time images regardless of whether a physical camera or a simulated camera stream is used. It allows for easy switching between hardware camera input and simulation environments.

## Architecture

- **Input Sources**
  - *Physical Camera*: devices identified by their serial number.
  - *Simulator Virtual Camera*: Network-accessible video stream provided by the Unity simulator.

- **Streaming and API**
  - The service publishes images/frames on a predefined topic or endpoint, allowing consumers (such as the web ui or vision modules) to subscribe and receive the camera feed.

## Configuration

### Setting Up the Environment

Before running the Camera Service, you need to create a `.env` file containing your environment variables. The easiest way to do this is by copying the provided example:

```bash
cd camera-service
cp .env.example .env
```

### Setting Up the Camera

#### Using a Real Camera

To use a physical camera, you need to provide its serial number in the configuration.

1. **Find your camera's serial number:**

   Plug in your camera and run:

   ```bash
   sudo udevadm info --query=all /dev/video1 | grep 'USB_SERIAL_SHORT'
   ```

   Replace `/dev/video1` with the correct device if needed.

2. **Update the serial number in [`camera-service/compose.yaml`](compose.yaml):**

   Edit the [camera compose.yaml](compose.yaml) configuration as follows:

   ```yaml
   configs:
     config_camera:
       content: |
         camera_serial_or_url: "<your_serial_number>" # e.g., "E2C32290"
   ```

   Replace `<your_serial_number>` with the value you obtained in the previous step.


### Wireless Reachy Mini camera

The wireless Reachy Mini's camera is served by the **reachy_booth** app, which
runs on the robot and reads the camera through the Reachy Mini Python SDK (see
[docs/wireless-reachy-booth-app.md](../docs/wireless-reachy-booth-app.md) to
install and start it). Point the service at the robot with a `reachy://` URL:

```yaml
configs:
  config_camera:
    content: |
      camera_serial_or_url: reachy://192.168.0.25   # robot IP, optional :port (default 8042)
      fps: 12
      reachy_stream_quality: 65
      streaming_resolution: {width: 640, height: 360}
      capture_resolution: {width: 1280, height: 720}
```

- Use the robot's IP: `reachy-mini.local` (mDNS) usually does not resolve inside
  containers. `curl http://<ip>:8042/health` from the host should work.
- The live stream (`camera_frame` topic, UI preview, tracking) is an MJPEG stream
  the robot encodes at `streaming_resolution`, `fps` and `reachy_stream_quality`.
  The defaults fit a weak Wi-Fi link (~0.3 MB/s); raise them on a good one.
- Photos (`/capture`) are fetched as a separate full-resolution still
  (`/camera/frame.jpg`), never older than 2 s. If that request fails, the newest
  stream frame is used and a warning is logged.
- The stream is read on a background thread over plain HTTP. A Wi-Fi hiccup
  shows up as lag; if the stream drops, the service reconnects with backoff
  (up to 10 s) and logs `Reachy video streaming` when video is back.

**Black screen in the UI** means no frames reach the UI server, which then
sends black. Check `docker compose logs camera` for `Reachy video unavailable`:
usually the reachy_booth app is not running on the robot. Start it from the
robot dashboard (`http://<ip>:8000`) and check `http://<ip>:8042/health`.

### Still-photo detection requirement

`GET /capture` now returns HTTP 409 if there is no fresh person detection
from the tracker, or the detection refers to an old camera frame. Keep the tracker
running until capture completes. This check applies to direct HTTP requests too;
preview streaming is unaffected. The photobooth's interaction manager searches
and checks human presence before acknowledging its capture tool.
