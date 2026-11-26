# ruff: noqa: E501, B023, E731, SIM115  (throwaway benchmark scripts)
"""Keep the FLUX.1 Kontext NIM busy with back-to-back renders (same request as the agent)."""

import argparse
import base64
import json
import time
import urllib.request

p = argparse.ArgumentParser()
p.add_argument("--url", default="http://localhost:9090/v1/infer")
p.add_argument("--image", required=True)
p.add_argument("--steps", type=int, default=20)
p.add_argument("--seconds", type=float, default=120)
a = p.parse_args()

img = base64.b64encode(open(a.image, "rb").read()).decode()
body = json.dumps(
    {
        "prompt": "make this person a pirate, oil painting",
        "aspect_ratio": "3:2",
        "resize_response_image": False,
        "image": f"data:image/png;base64,{img}",
        "steps": a.steps,
        "disable_safety_checker": True,
    }
).encode()

end = time.time() + a.seconds
while time.time() < end:
    t = time.time()
    req = urllib.request.Request(a.url, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        r.read()
    print(
        json.dumps(
            {
                "flux_render_s": round(time.time() - t, 1),
                "steps": a.steps,
                "t_start": round(t, 1),
                "t_end": round(time.time(), 1),
            }
        ),
        flush=True,
    )
