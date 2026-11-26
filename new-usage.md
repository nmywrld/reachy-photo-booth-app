The booth is now a magic mirror: a stylized live feed, with styles changed by voice and photos taken with an on-screen shutter.

## 1. One-time setup
1. **Put the app on the robot.** The `reachy_booth` app has to be running on the Reachy. That part hasn't changed; see [docs/wireless-reachy-booth-app.md](docs/wireless-reachy-booth-app.md).
2. **Point the stack at the robot.** Run `scripts/reachy-ip.sh` to put its address in `.env` as `REACHY_HOST`.
3. **Check `.env`.** You need `NVIDIA_API_KEY` and `HF_TOKEN`, plus the `EXTERNAL_MINIO_*` variables, which are used for the QR-code download page. Yours are already set.

## 2. Start the booth
```bash
docker compose up -d
```
- **First start:** the mirror downloads SD-Turbo and builds its TensorRT engines, which takes about 90 seconds once the LLM is up. Later starts take about 15 seconds.
- **Check it's ready:** `docker ps` should show `mirror`, `agent`, `llm`, `image-generator` and `riva` as **healthy**. `curl localhost:7072/health` should return `{"backend": "trt"}`.

## 3. Open the screens
| Screen | URL |
|---|---|
| **Kiosk** (show it full-screen on the booth display) | http://localhost:3001 |
| Model wall (which models are working, GPU memory) | http://localhost:9100 |
| Latest mirror frame (for debugging) | http://localhost:7072/frame.jpg |

## 4. What a visitor does
1. **Walks up.** The screen is always a live mirror. With nobody chosen a style, it cycles through eight looks every 20 seconds.
2. **Talks to Reachy.** Speaking starts the conversation, for example "Make me a pirate" or "Anime style please". Reachy changes the mirror within a second and replies. They can change styles as often as they like.
3. **Takes the photo** in any of three ways: tap the round **shutter button** (bottom right), press **Enter** on a keyboard or clicker, or say "take a picture".
4. **3-second countdown, then the flash.** About 1–3 s later the photo appears with a **QR code**, and Reachy tells them to scan it.
5. **Hi-res version.** The mirror freezes for about 45 s while Flux paints a high-resolution version. That version then replaces the instant photo on screen and on the phone's download page. Links expire after 30 minutes.
6. **Leaves.** Their chosen style resets to the rotating looks.

## 5. Settings you might change
| What | Where |
|---|---|
| Style strength (lower keeps faces more recognisable), idle styles, pause during renders | `config_mirror` in [mirror-service/compose.yaml](mirror-service/compose.yaml) |
| Countdown length (`mirror_countdown_seconds`), head tracking | `PhotoBoothBotConfig` in [interaction-manager-service/src/configuration.py](interaction-manager-service/src/configuration.py) |
| How long the photo stays on screen (`photo_display_seconds`) | [ui-server-service/src/configuration.py](ui-server-service/src/configuration.py) |
| What Reachy says, and the safety rules | [agent-service/src/configs/photobooth.yml](agent-service/src/configs/photobooth.yml) |
| Download link lifetime (`link_expires`) | `MirrorPhotoConfig` in [mirror_photo.py](agent-service/workflows/photo_booth_agent/src/photo_booth_agent/mirror_photo.py) (only in code for now) |

After editing a config file, run `docker compose up -d <service>`. After code changes, run `docker compose build <service>` first.

## 6. Testing without the robot
If the robot is off, `robot-controller` is unhealthy, which blocks the interaction manager from starting. To test with a still photo in place of the camera:
```bash
docker compose up -d --no-deps interaction-manager
docker compose stop camera && docker rm camera
docker run --rm -d --name camera --hostname camera --network reachy-photo-booth-app_default \
  -p 7071:7071 -v $PWD/scripts:/scripts:ro -v /path/to/person.jpg:/person.jpg:ro \
  --entrypoint python camera:latest /scripts/fake_camera.py /person.jpg
```
To go back to the real camera: `docker stop camera && docker compose up -d camera`.

## 7. If something's off
- **Mirror black or raw camera only:** `docker logs mirror`. A stats line every 30 s shows fps and delay.
- **Shutter does nothing:** the camera must see a person (`docker logs tracker` should show `USER_APPEARED`), then check `docker logs interaction-manager`.
- **No QR code or hi-res photo:** `docker logs agent | grep "Mirror photo"`.

## Not tested yet
The full setup hasn't run on the real robot yet, and nobody has talked to it through the microphone. My tests used the stand-in camera and sent the voice tools' messages directly. Your first session with the Reachy online is the real end-to-end test.

Nothing is committed yet, and `.env.example` and the speech-to-text config are still staged as they were. If you'd like this guide as a page to share with the team, I can publish it.