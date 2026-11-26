# ruff: noqa: E501, B023, E731, SIM115  (throwaway benchmark scripts)
"""Magic-mirror spike: how fast can SD-Turbo img2img + TAESD stylize frames on this GPU?

A minimal StreamDiffusion-style loop (no StreamDiffusion dependency):
  JPEG -> 512x512 tensor -> TAESD encode -> add fixed noise at timestep t
  -> SD-Turbo UNet (1 or 2 steps) -> x0 -> TAESD decode -> JPEG

Backends:
  eager    plain PyTorch fp16
  compile  torch.compile (inductor) of UNet + TAESD
  trt      torch-tensorrt (dynamo IR) of UNet + TAESD, static 512x512 shapes

Prints one JSON line with fps / latency / memory, and writes sample frames.
"""

from __future__ import annotations

import argparse
import io
import json
import statistics
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

MODEL = "stabilityai/sd-turbo"
TAESD = "madebyollin/taesd"
DT = torch.float16  # set from --dtype in main()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--backend", choices=["eager", "compile", "trt"], default="eager")
    p.add_argument("--steps", type=int, default=1, choices=[1, 2])
    p.add_argument("--size", type=int, default=512)
    p.add_argument("--strength", type=float, default=0.5, help="img2img strength")
    p.add_argument("--frames", type=int, default=200)
    p.add_argument("--warmup", type=int, default=20)
    p.add_argument("--input", type=Path, required=True, help="source image (a person)")
    p.add_argument(
        "--prompt", default="portrait of a pirate, oil painting, dramatic light"
    )
    p.add_argument("--out", type=Path, default=Path("/out"))
    p.add_argument("--tag", default="")
    p.add_argument("--channels-last", action="store_true")
    p.add_argument("--dtype", choices=["fp16", "bf16"], default="fp16")
    return p.parse_args()


class Mirror(torch.nn.Module):
    """One forward = one stylized frame, all on GPU, fp16."""

    def __init__(
        self, unet, vae, alphas_cumprod, timesteps, prompt_embeds, size, v_pred
    ):
        super().__init__()
        self.unet = unet
        self.vae = vae
        self.v_pred = v_pred
        self.timesteps = timesteps  # descending ints, len == steps
        a = alphas_cumprod[timesteps].to(DT)
        self.register_buffer("sqrt_a", a.sqrt().view(-1, 1, 1, 1))
        self.register_buffer("sqrt_1ma", (1 - a).sqrt().view(-1, 1, 1, 1))
        self.register_buffer("t", torch.tensor(timesteps, dtype=torch.long))
        self.register_buffer("emb", prompt_embeds)
        g = torch.Generator(device="cuda").manual_seed(0)
        lat = size // 8
        # Fixed noise every frame: much less flicker than fresh noise.
        self.register_buffer(
            "noise",
            torch.randn(
                (len(timesteps), 4, lat, lat), generator=g, device="cuda", dtype=DT
            ),
        )

    def forward(self, img: torch.Tensor) -> torch.Tensor:
        # img: (1,3,H,W) in [0,1]
        x0 = self.vae.encoder(img * 2 - 1)  # TAESD encoder works on [-1,1]
        for i in range(len(self.timesteps)):
            xt = self.sqrt_a[i] * x0 + self.sqrt_1ma[i] * self.noise[i : i + 1]
            out = self.unet(
                xt, self.t[i], encoder_hidden_states=self.emb, return_dict=False
            )[0]
            if self.v_pred:
                x0 = self.sqrt_a[i] * xt - self.sqrt_1ma[i] * out
            else:
                x0 = (xt - self.sqrt_1ma[i] * out) / self.sqrt_a[i]
        y = self.vae.decoder(x0)
        return ((y + 1) / 2).clamp(0, 1)


def load(args):
    from diffusers import AutoencoderTiny, AutoPipelineForImage2Image

    pipe = AutoPipelineForImage2Image.from_pretrained(
        MODEL, torch_dtype=DT, variant="fp16"
    )  # fp16 weights, cast to DT
    pipe.to("cuda")
    with torch.no_grad():
        emb, _ = pipe.encode_prompt(args.prompt, "cuda", 1, False)
    vae = AutoencoderTiny.from_pretrained(TAESD, torch_dtype=DT).to("cuda")
    sched = pipe.scheduler
    v_pred = sched.config.get("prediction_type", "epsilon") == "v_prediction"
    # img2img strength -> starting timestep; 2 steps splits the remaining range.
    t0 = int(999 * args.strength)
    ts = [t0] if args.steps == 1 else [t0, t0 // 2]
    m = Mirror(
        pipe.unet.eval(),
        vae.eval(),
        sched.alphas_cumprod.cuda(),
        ts,
        emb.to(DT),
        args.size,
        v_pred,
    )
    if args.channels_last:  # 3x slower with cuDNN 9.10 on GB10; test per stack
        m.unet.to(memory_format=torch.channels_last)
        m.vae.to(memory_format=torch.channels_last)
    del pipe.text_encoder, pipe.vae
    return m, {"timesteps": ts, "prediction_type": sched.config.get("prediction_type")}


def accelerate(m: Mirror, backend: str, size: int) -> Mirror:
    if backend == "eager":
        return m
    if backend == "compile":
        m.unet = torch.compile(
            m.unet, mode="max-autotune-no-cudagraphs", fullgraph=True
        )
        m.vae.encoder = torch.compile(m.vae.encoder, mode="max-autotune-no-cudagraphs")
        m.vae.decoder = torch.compile(m.vae.decoder, mode="max-autotune-no-cudagraphs")
        return m
    import torch_tensorrt

    lat = size // 8

    class UNetWrap(torch.nn.Module):
        def __init__(self, unet):
            super().__init__()
            self.unet = unet

        def forward(self, x, t, e):
            return self.unet(x, t, encoder_hidden_states=e, return_dict=False)[0]

    def trt(mod, inputs):
        return torch_tensorrt.compile(
            mod,
            ir="dynamo",
            inputs=inputs,
            enabled_precisions={DT},
            use_explicit_typing=False,
            min_block_size=1,
            truncate_double=True,
        )

    with torch.no_grad():
        uw = trt(
            UNetWrap(m.unet),
            [
                torch.randn(1, 4, lat, lat, device="cuda", dtype=DT),
                m.t[0].clone(),
                m.emb,
            ],
        )
        enc = trt(
            m.vae.encoder, [torch.randn(1, 3, size, size, device="cuda", dtype=DT)]
        )
        dec = trt(m.vae.decoder, [torch.randn(1, 4, lat, lat, device="cuda", dtype=DT)])

    class TRTUNet(torch.nn.Module):
        def forward(self, x, t, encoder_hidden_states, return_dict=False):
            return (uw(x, t, encoder_hidden_states),)

    m.unet = TRTUNet()
    m.vae.encoder = enc
    m.vae.decoder = dec
    return m


def center_crop_square(im: Image.Image, size: int) -> Image.Image:
    w, h = im.size
    s = min(w, h)
    return im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize(
        (size, size)
    )


def make_frames(src: Path, n: int) -> list[bytes]:
    """Simulated 640x360 camera JPEGs with small per-frame jitter (no two identical)."""
    # Fit the whole portrait into the middle of a 16:9 frame, like a person
    # standing centred in front of the robot camera.
    im = Image.open(src).convert("RGB")
    im.thumbnail((384, 384))
    base = Image.new("RGB", (680, 384), (128, 128, 128))
    base.paste(im, ((680 - im.width) // 2, (384 - im.height) // 2))
    out = []
    for i in range(n):
        dx, dy = int(20 + 20 * np.sin(i / 7)), int(12 + 12 * np.cos(i / 5))
        buf = io.BytesIO()
        base.crop((dx, dy, dx + 640, dy + 360)).save(buf, "JPEG", quality=65)
        out.append(buf.getvalue())
    return out


def main() -> None:
    global DT
    args = parse_args()
    DT = torch.bfloat16 if args.dtype == "bf16" else torch.float16
    args.out.mkdir(parents=True, exist_ok=True)
    torch.backends.cudnn.benchmark = True
    free0, total = torch.cuda.mem_get_info()

    t_load = time.perf_counter()
    m, info = load(args)
    m = accelerate(m, args.backend, args.size)
    frames = make_frames(args.input, args.warmup + args.frames)
    build_s = None

    gpu_ms, e2e_ms = [], []
    with torch.inference_mode():
        for i, jpg in enumerate(frames):
            if i == args.warmup:
                build_s = time.perf_counter() - t_load
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
                wall0 = time.perf_counter()
                t_start = time.time()
            s0 = time.perf_counter()
            im = center_crop_square(
                Image.open(io.BytesIO(jpg)).convert("RGB"), args.size
            )
            x = (
                torch.from_numpy(np.asarray(im)).cuda().permute(2, 0, 1)[None].to(DT)
                / 255
            )
            ev0, ev1 = (
                torch.cuda.Event(enable_timing=True),
                torch.cuda.Event(enable_timing=True),
            )
            ev0.record()
            if args.channels_last:
                x = x.contiguous(memory_format=torch.channels_last)
            y = m(x)
            ev1.record()
            arr = (y[0].permute(1, 2, 0) * 255).byte().cpu().numpy()
            buf = io.BytesIO()
            Image.fromarray(arr).save(buf, "JPEG", quality=80)
            e2e = (time.perf_counter() - s0) * 1000
            if i >= args.warmup:
                gpu_ms.append(ev0.elapsed_time(ev1))
                e2e_ms.append(e2e)
            if i in (args.warmup, args.warmup + args.frames // 2):
                tag = f"{args.backend}_{args.dtype}_s{args.steps}_str{args.strength}{args.tag}_{i}"
                im.save(args.out / f"{tag}_in.jpg")
                (args.out / f"{tag}_out.jpg").write_bytes(buf.getvalue())
        wall = time.perf_counter() - wall0

    free1, _ = torch.cuda.mem_get_info()
    q = lambda v, p: float(np.percentile(v, p))
    print(
        json.dumps(
            {
                "backend": args.backend,
                "steps": args.steps,
                "size": args.size,
                "strength": args.strength,
                "tag": args.tag,
                "dtype": args.dtype,
                **info,
                "fps": round(args.frames / wall, 1),
                "gpu_ms_p50": round(statistics.median(gpu_ms), 1),
                "gpu_ms_p95": round(q(gpu_ms, 95), 1),
                "e2e_ms_p50": round(statistics.median(e2e_ms), 1),
                "e2e_ms_p95": round(q(e2e_ms, 95), 1),
                "peak_alloc_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2),
                "process_used_gb": round((free0 - free1) / 1e9, 2),
                "system_free_gb_after": round(free1 / 1e9, 1),
                "total_gb": round(total / 1e9, 1),
                "build_s": round(build_s or 0, 1),
                "t_start": round(t_start, 1),
                "t_end": round(time.time(), 1),
            }
        )
    )


if __name__ == "__main__":
    main()
