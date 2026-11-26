# Spike image: NGC PyTorch (torch, cuDNN, TensorRT and torch-tensorrt for GB10) + diffusers.
FROM nvcr.io/nvidia/pytorch:26.10-py3
# NGC's torchao is newer than diffusers 0.35 expects and breaks its import; not needed here.
RUN pip install --no-cache-dir diffusers==0.35.1 transformers==4.55.0 accelerate==1.10.1 \
 && pip uninstall -y torchao
