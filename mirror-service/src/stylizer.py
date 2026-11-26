# SPDX-License-Identifier: Apache-2.0
"""SD-Turbo img2img + TAESD, 1-2 denoising steps per frame (StreamDiffusion-style).

JPEG -> centre square crop -> TAESD encode -> fixed noise at timestep t
-> SD-Turbo UNet -> x0 -> TAESD decode -> JPEG

Measured on GB10 with NGC PyTorch 26.10 at 512x512, 1 step, LLM + Flux loaded:
TensorRT ~32 fps (31 ms), torch.compile ~24 fps, eager ~17 fps.
"""

from __future__ import annotations

import io
import logging
import threading
from pathlib import Path

import numpy as np
import torch
from PIL import Image

logger = logging.getLogger("mirror")


class _Pipeline(torch.nn.Module):
    """One forward = one stylized frame, all on the GPU."""

    def __init__(self, unet, vae, alphas_cumprod, timesteps, size, dtype, v_pred):
        super().__init__()
        self.unet = unet
        self.vae = vae
        self.v_pred = v_pred
        self.steps = len(timesteps)
        a = alphas_cumprod[timesteps].to(dtype)
        self.register_buffer("sqrt_a", a.sqrt().view(-1, 1, 1, 1))
        self.register_buffer("sqrt_1ma", (1 - a).sqrt().view(-1, 1, 1, 1))
        self.register_buffer("t", torch.tensor(timesteps, dtype=torch.long))
        g = torch.Generator(device="cuda").manual_seed(0)
        lat = size // 8
        # The same noise every frame: much less flicker than fresh noise.
        self.register_buffer(
            "noise",
            torch.randn(
                (self.steps, 4, lat, lat), generator=g, device="cuda", dtype=dtype
            ),
        )

    def forward(self, img: torch.Tensor, emb: torch.Tensor) -> torch.Tensor:
        x0 = self.vae.encoder(img * 2 - 1)  # TAESD works in [-1, 1]
        for i in range(self.steps):
            xt = self.sqrt_a[i] * x0 + self.sqrt_1ma[i] * self.noise[i : i + 1]
            out = self.unet(
                xt, self.t[i], encoder_hidden_states=emb, return_dict=False
            )[0]
            if self.v_pred:
                x0 = self.sqrt_a[i] * xt - self.sqrt_1ma[i] * out
            else:
                x0 = (xt - self.sqrt_1ma[i] * out) / self.sqrt_a[i]
        return ((self.vae.decoder(x0) + 1) / 2).clamp(0, 1)


class _UNetArgs(torch.nn.Module):
    """Positional-only UNet wrapper so it can be exported / compiled to TensorRT."""

    def __init__(self, unet):
        super().__init__()
        self.unet = unet

    def forward(self, x, t, e):
        return self.unet(x, t, encoder_hidden_states=e, return_dict=False)[0]


class _CompiledUNet(torch.nn.Module):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def forward(self, x, t, encoder_hidden_states, return_dict=False):
        return (self.fn(x, t, encoder_hidden_states),)


class Stylizer:
    def __init__(
        self,
        model: str,
        taesd: str,
        backend: str = "trt",
        dtype: str = "bf16",
        steps: int = 1,
        strength: float = 0.5,
        size: int = 512,
        jpeg_quality: int = 80,
        engine_cache_dir: Path | None = None,
    ) -> None:
        from diffusers import AutoencoderTiny, AutoPipelineForImage2Image

        self.size = size
        self.jpeg_quality = jpeg_quality
        self.dtype = torch.bfloat16 if dtype == "bf16" else torch.float16
        self._lock = threading.Lock()

        pipe = AutoPipelineForImage2Image.from_pretrained(
            model, torch_dtype=self.dtype, variant="fp16"
        ).to("cuda")
        vae = AutoencoderTiny.from_pretrained(taesd, torch_dtype=self.dtype).to("cuda")
        self._tokenizer = pipe.tokenizer
        self._text_encoder = pipe.text_encoder.eval()
        sched = pipe.scheduler
        v_pred = sched.config.get("prediction_type", "epsilon") == "v_prediction"
        t0 = int(999 * strength)
        timesteps = [t0] if steps == 1 else [t0, t0 // 2]
        self._pipe = _Pipeline(
            pipe.unet.eval(),
            vae.eval(),
            sched.alphas_cumprod.cuda(),
            timesteps,
            size,
            self.dtype,
            v_pred,
        )
        del pipe  # keep only the parts used per frame / per style
        self._emb = self._embed("")

        tag = f"{model.replace('/', '_')}_{dtype}_{size}"
        self.backend = self._accelerate(backend, engine_cache_dir, tag)
        logger.info(
            f"Stylizer ready: backend={self.backend} steps={steps} t={timesteps}"
        )

    @torch.inference_mode()
    def _embed(self, prompt: str) -> torch.Tensor:
        # Same as the pipeline's encode_prompt for SD 2.x without CFG/clip-skip.
        ids = self._tokenizer(
            prompt,
            padding="max_length",
            truncation=True,
            max_length=self._tokenizer.model_max_length,
            return_tensors="pt",
        ).input_ids.to("cuda")
        return self._text_encoder(ids)[0].to(self.dtype)

    def _accelerate(self, backend: str, cache_dir: Path | None, tag: str) -> str:
        if backend == "eager":
            return "eager"
        if backend == "trt":
            try:
                self._to_tensorrt(cache_dir, tag)
                return "trt"
            except Exception:
                logger.exception("TensorRT failed; falling back to torch.compile")
        p = self._pipe
        p.unet = torch.compile(
            p.unet, mode="max-autotune-no-cudagraphs", fullgraph=True
        )
        p.vae.encoder = torch.compile(p.vae.encoder, mode="max-autotune-no-cudagraphs")
        p.vae.decoder = torch.compile(p.vae.decoder, mode="max-autotune-no-cudagraphs")
        return "compile"

    def _to_tensorrt(self, cache_dir: Path | None, tag: str) -> None:
        import torch_tensorrt

        lat = self.size // 8
        p = self._pipe
        parts = {
            "unet": (
                _UNetArgs(p.unet),
                (
                    torch.randn(1, 4, lat, lat, device="cuda", dtype=self.dtype),
                    p.t[0].clone(),
                    self._emb,
                ),
            ),
            "taesd_enc": (
                p.vae.encoder,
                (
                    torch.randn(
                        1, 3, self.size, self.size, device="cuda", dtype=self.dtype
                    ),
                ),
            ),
            "taesd_dec": (
                p.vae.decoder,
                (torch.randn(1, 4, lat, lat, device="cuda", dtype=self.dtype),),
            ),
        }
        built = {}
        with torch.inference_mode():
            for name, (module, inputs) in parts.items():
                path = cache_dir / f"{tag}_{name}.ep" if cache_dir else None
                if path is not None and path.exists():
                    try:
                        built[name] = torch_tensorrt.load(str(path)).module()
                        logger.info(f"Loaded cached TensorRT engine {path.name}")
                        continue
                    except Exception:
                        logger.exception(
                            f"Cached engine {path.name} unusable; rebuilding"
                        )
                logger.info(f"Building TensorRT engine for {name} (takes 1-4 min)...")
                trt = torch_tensorrt.compile(
                    module,
                    ir="dynamo",
                    inputs=list(inputs),
                    enabled_precisions={self.dtype},
                    use_explicit_typing=False,
                    min_block_size=1,
                    truncate_double=True,
                )
                if path is not None:
                    try:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        torch_tensorrt.save(trt, str(path), arg_inputs=list(inputs))
                    except Exception:
                        logger.exception(f"Could not cache engine {path.name}")
                built[name] = trt
        p.unet = _CompiledUNet(built["unet"])
        p.vae.encoder = built["taesd_enc"]
        p.vae.decoder = built["taesd_dec"]

    def set_style(self, prompt: str) -> None:
        emb = self._embed(prompt)
        with self._lock:
            self._emb = emb

    def _square(self, jpeg: bytes) -> Image.Image:
        im = Image.open(io.BytesIO(jpeg)).convert("RGB")
        w, h = im.size
        s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
        return im.resize((self.size, self.size), Image.Resampling.BILINEAR)

    @torch.inference_mode()
    def stylize_jpeg(self, jpeg: bytes) -> bytes:
        im = self._square(jpeg)
        x = torch.from_numpy(np.array(im)).cuda().permute(2, 0, 1)[None]
        x = x.to(self.dtype) / 255
        with self._lock:
            y = self._pipe(x, self._emb)
        arr = (y[0].permute(1, 2, 0).float() * 255).round().byte().cpu().numpy()
        buf = io.BytesIO()
        Image.fromarray(arr).save(buf, "JPEG", quality=self.jpeg_quality)
        return buf.getvalue()
