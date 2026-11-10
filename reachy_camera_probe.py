#!/usr/bin/env python3
"""Probe the wireless Reachy Mini camera over WebRTC.

Connects to the daemon's local signalling server (ws://<host>:8443), negotiates a
WebRTC session as a consumer, and reports what the camera delivers: codec, frame
size, pixel format, timestamps and the measured frame rate. Optionally saves a few
frames as JPEG so you can look at them.

It is a standalone exploration tool (nothing in the services imports it). The
camera service can reuse the same handshake once we know what the stream looks like.

Usage:
    uv run --with aiortc --with websockets --with opencv-python-headless \\
        --with numpy python reachy_camera_probe.py
    python reachy_camera_probe.py --host 192.168.0.25 --frames 120 --save 3

Protocol (GStreamer webrtcsink signalling, JSON over WebSocket):
    <- welcome {peerId}
    -> list                      <- list {producers: [{id, meta: {name}}]}
    -> startSession {peerId}     <- sessionStarted {sessionId}
    <- peer {sdp: offer}         -> peer {sdp: answer}
    <-> peer {ice: {...}}        (trickle ICE both ways)
"""

import argparse
import asyncio
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import cv2
import websockets
from aiortc import RTCConfiguration, RTCPeerConnection, RTCSessionDescription
from aiortc.rtcdtlstransport import RTCCertificate
from aiortc.sdp import candidate_from_sdp

PRODUCER_NAME = "reachymini"


def patch_dtls_ciphers() -> None:
    """Let aiortc complete DTLS with the robot's GStreamer webrtcsink.

    aiortc's default DTLS cipher list shares no cipher with the robot, so the
    connection never reaches "connected". Same shim as the Reachy Mini SDK uses.
    """
    original = RTCCertificate._create_ssl_context

    def patched(self: Any, *args: Any, **kwargs: Any) -> Any:
        ctx = original(self, *args, **kwargs)
        ctx.set_cipher_list(
            b"ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:"
            b"ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:"
            b"ECDHE-RSA-AES128-GCM-SHA256"
        )
        return ctx

    RTCCertificate._create_ssl_context = patched  # type: ignore[method-assign]


def fetch_daemon_info(host: str, port: int) -> None:
    """Print camera specs and media status from the daemon REST API."""
    for path in ("/api/media/status", "/api/camera/specs"):
        try:
            with urllib.request.urlopen(f"http://{host}:{port}{path}", timeout=5) as r:
                data = json.load(r)
        except Exception as exc:  # noqa: BLE001 - diagnostic tool
            print(f"[daemon] {path}: unavailable ({exc})")
            continue
        if path.endswith("specs"):
            res = ", ".join(
                f"{r['width']}x{r['height']}@{r['fps']}"
                for r in data.get("available_resolutions", [])
            )
            default = data.get("default_resolution", {}).get("name")
            print(f"[daemon] camera={data.get('name')} default={default}")
            print(f"[daemon] resolutions: {res}")
        else:
            print(f"[daemon] media status: {data}")


async def run(args: argparse.Namespace) -> int:
    patch_dtls_ciphers()
    out_dir = Path(args.out)
    if args.save:
        out_dir.mkdir(parents=True, exist_ok=True)

    # LAN only: host candidates are enough, no STUN/TURN needed.
    pc = RTCPeerConnection(RTCConfiguration(iceServers=[]))
    done = asyncio.Event()
    connected = asyncio.Event()
    stats: dict[str, Any] = {"arrivals": [], "pts": [], "saved": 0}

    @pc.on("connectionstatechange")
    async def on_state() -> None:
        print(f"[webrtc] connection state: {pc.connectionState}")
        if pc.connectionState == "connected":
            connected.set()
        elif pc.connectionState in ("failed", "closed"):
            done.set()

    @pc.on("track")
    def on_track(track: Any) -> None:
        print(f"[webrtc] track received: kind={track.kind}")
        if track.kind == "video":
            asyncio.ensure_future(consume_video(track))

    async def consume_video(track: Any) -> None:
        first = True
        for i in range(args.frames):
            frame = await track.recv()  # av.VideoFrame
            now = time.monotonic()
            stats["arrivals"].append(now)
            stats["pts"].append(frame.pts)
            if first:
                first = False
                print(
                    f"[video] first frame: {frame.width}x{frame.height} "
                    f"format={frame.format.name} time_base={frame.time_base}"
                )
            if i < args.save:
                img = frame.to_ndarray(format="bgr24")  # what the service would use
                path = out_dir / f"frame_{i:03d}.jpg"
                cv2.imwrite(str(path), img)
                stats["saved"] += 1
                if i == 0:
                    print(
                        f"[video] ndarray: shape={img.shape} dtype={img.dtype} "
                        f"(BGR, same layout cv2.VideoCapture.read() returns)"
                    )
        done.set()

    async with websockets.connect(f"ws://{args.host}:{args.signalling_port}") as ws:
        welcome = json.loads(await ws.recv())
        print(f"[signalling] connected, our peerId={welcome.get('peerId')}")

        await ws.send(json.dumps({"type": "list"}))
        producers = json.loads(await ws.recv()).get("producers", [])
        print(f"[signalling] producers: {[p['meta'] for p in producers]}")
        producer = next(
            (p["id"] for p in producers if p["meta"].get("name") == PRODUCER_NAME),
            None,
        )
        if producer is None:
            print(f"error: no producer named {PRODUCER_NAME!r}", file=sys.stderr)
            return 1

        await ws.send(json.dumps({"type": "startSession", "peerId": producer}))
        session_id: str | None = None

        async def signalling_loop() -> None:
            nonlocal session_id
            async for raw in ws:
                msg = json.loads(raw)
                kind = msg.get("type")
                if kind == "sessionStarted":
                    session_id = msg["sessionId"]
                elif kind == "peer":
                    if "sdp" in msg:
                        sdp = msg["sdp"]
                        print(f"[signalling] got SDP {sdp['type']}")
                        await pc.setRemoteDescription(
                            RTCSessionDescription(sdp["sdp"], sdp["type"])
                        )
                        await pc.setLocalDescription(await pc.createAnswer())
                        await ws.send(
                            json.dumps(
                                {
                                    "type": "peer",
                                    "sessionId": session_id,
                                    "sdp": {
                                        "type": "answer",
                                        "sdp": pc.localDescription.sdp,
                                    },
                                }
                            )
                        )
                    elif msg.get("ice", {}).get("candidate"):
                        ice = msg["ice"]
                        cand = ice["candidate"].removeprefix("candidate:")
                        candidate = candidate_from_sdp(cand)
                        candidate.sdpMid = None
                        candidate.sdpMLineIndex = ice.get("sdpMLineIndex", 0)
                        await pc.addIceCandidate(candidate)
                elif kind == "endSession":
                    print("[signalling] robot ended the session")
                    done.set()
                    return

        sig_task = asyncio.ensure_future(signalling_loop())
        try:
            await asyncio.wait_for(connected.wait(), timeout=args.timeout)
            await asyncio.wait_for(done.wait(), timeout=args.timeout + args.frames)
        except TimeoutError:
            print("error: timed out waiting for the WebRTC stream", file=sys.stderr)
        finally:
            sig_task.cancel()
            await pc.close()

    report(stats, out_dir if args.save else None)
    return 0 if stats["arrivals"] else 2


def report(stats: dict[str, Any], out_dir: Path | None) -> None:
    arrivals = stats["arrivals"]
    print("\n=== summary ===")
    print(f"frames received: {len(arrivals)}")
    if len(arrivals) < 2:
        return
    gaps = [b - a for a, b in zip(arrivals, arrivals[1:], strict=False)]
    span = arrivals[-1] - arrivals[0]
    print(f"measured fps: {(len(arrivals) - 1) / span:.1f}")
    print(
        f"inter-frame gap ms: mean={statistics.mean(gaps) * 1000:.1f} "
        f"max={max(gaps) * 1000:.1f}"
    )
    if out_dir:
        print(f"saved {stats['saved']} frame(s) to {out_dir}/")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--host", default="reachy-mini.local", help="robot hostname or IP")
    p.add_argument("--daemon-port", type=int, default=8000)
    p.add_argument("--signalling-port", type=int, default=8443)
    p.add_argument("--frames", type=int, default=60, help="frames to receive")
    p.add_argument("--save", type=int, default=1, help="save the first N frames")
    p.add_argument("--out", default="probe-out", help="directory for saved frames")
    p.add_argument("--timeout", type=float, default=20, help="connect timeout (s)")
    args = p.parse_args()

    fetch_daemon_info(args.host, args.daemon_port)
    return asyncio.run(run(args))


if __name__ == "__main__":
    sys.exit(main())
