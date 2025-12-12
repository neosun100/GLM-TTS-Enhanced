FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

# Install cuDNN 9 for ONNX Runtime
RUN apt-get update && apt-get install -y wget gnupg2 && \
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb && \
    dpkg -i cuda-keyring_1.1-1_all.deb && \
    apt-get update && \
    apt-get install -y libcudnn9-cuda-12 libcudnn9-dev-cuda-12 && \
    rm cuda-keyring_1.1-1_all.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir $(grep -v "^torch" requirements.txt | grep -v "^#") && \
    pip3 install --no-cache-dir flask flasgger flask-cors onnxruntime-gpu

COPY . .

ENV PORT=8080
ENV GPU_IDLE_TIMEOUT=60
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

CMD ["python3", "server.py"]
