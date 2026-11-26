# ruff: noqa: E501, B023, E731, SIM115  (throwaway benchmark scripts)
"""Is cuDNN conv the bottleneck on GB10? TAESD decoder under different settings."""

import torch
from diffusers import AutoencoderTiny
from profile_parts import bench  # noqa: E402  (re-runs matmul header; fine)

print("cudnn", torch.backends.cudnn.version())
vae = (
    AutoencoderTiny.from_pretrained("madebyollin/taesd", torch_dtype=torch.float16)
    .cuda()
    .eval()
)
lat = torch.randn(1, 4, 64, 64, device="cuda", dtype=torch.half)
with torch.inference_mode():
    for bm in (False, True):
        for cl in (False, True):
            torch.backends.cudnn.benchmark = bm
            v = vae.to(
                memory_format=torch.channels_last if cl else torch.contiguous_format
            )
            x = lat.contiguous(memory_format=torch.channels_last) if cl else lat
            print(
                f"dec benchmark={bm} channels_last={cl}: {bench(lambda: v.decoder(x)):.1f} ms"
            )
    torch.backends.cudnn.enabled = False
    print(f"dec cudnn disabled: {bench(lambda: vae.decoder(lat)):.1f} ms")
    torch.backends.cudnn.enabled = True
    vb = vae.to(torch.bfloat16, memory_format=torch.channels_last)
    print(
        f"dec bf16 channels_last: {bench(lambda: vb.decoder(lat.bfloat16().contiguous(memory_format=torch.channels_last))):.1f} ms"
    )
    c = torch.nn.Conv2d(64, 64, 3, padding=1).cuda().half()
    y = torch.randn(1, 64, 512, 512, device="cuda", dtype=torch.half)
    ms = bench(lambda: c(y))
    print(
        f"single 3x3 conv 64ch @512: {ms:.2f} ms = {2 * 64 * 64 * 9 * 512 * 512 / ms / 1e9:.1f} TFLOPS"
    )
