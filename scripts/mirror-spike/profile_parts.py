# ruff: noqa: E501, B023, E731, SIM115  (throwaway benchmark scripts)
"""Where does the frame time go? Raw matmul TFLOPS, then UNet / TAESD encode / decode alone."""

import torch
from diffusers import AutoencoderTiny, UNet2DConditionModel


def bench(fn, n=30):
    for _ in range(5):
        fn()
    torch.cuda.synchronize()
    a, b = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    a.record()
    for _ in range(n):
        fn()
    b.record()
    torch.cuda.synchronize()
    return a.elapsed_time(b) / n


with torch.inference_mode():
    for dt in (torch.float16, torch.bfloat16):
        x = torch.randn(8192, 8192, device="cuda", dtype=dt)
        ms = bench(lambda: x @ x, 20)
        print(f"matmul {dt}: {2 * 8192**3 / ms / 1e9:.1f} TFLOPS")

    unet = (
        UNet2DConditionModel.from_pretrained(
            "stabilityai/sd-turbo",
            subfolder="unet",
            torch_dtype=torch.float16,
            variant="fp16",
        )
        .cuda()
        .eval()
    )
    vae = (
        AutoencoderTiny.from_pretrained("madebyollin/taesd", torch_dtype=torch.float16)
        .cuda()
        .eval()
    )
    lat = torch.randn(1, 4, 64, 64, device="cuda", dtype=torch.half)
    emb = torch.randn(1, 77, 1024, device="cuda", dtype=torch.half)
    img = torch.randn(1, 3, 512, 512, device="cuda", dtype=torch.half)
    t = torch.tensor(499, device="cuda")
    print("unet ms", round(bench(lambda: unet(lat, t, encoder_hidden_states=emb)), 1))
    print("taesd enc ms", round(bench(lambda: vae.encoder(img)), 1))
    print("taesd dec ms", round(bench(lambda: vae.decoder(lat)), 1))
    unet.set_attn_processor(
        __import__("diffusers").models.attention_processor.AttnProcessor()
    )
    print(
        "unet (no SDPA) ms",
        round(bench(lambda: unet(lat, t, encoder_hidden_states=emb)), 1),
    )
