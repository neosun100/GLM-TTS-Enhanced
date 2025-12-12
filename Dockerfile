# GLM-TTS Enhanced v2.1.2 - All-in-One Docker Image
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies and cuDNN 9
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    && wget https://developer.download.nvidia.com/compute/cudnn/9.0.0/local_installers/cudnn-local-repo-ubuntu2204-9.0.0_1.0-1_amd64.deb \
    && dpkg -i cudnn-local-repo-ubuntu2204-9.0.0_1.0-1_amd64.deb \
    && cp /var/cudnn-local-repo-ubuntu2204-9.0.0/cudnn-*-keyring.gpg /usr/share/keyrings/ \
    && apt-get update \
    && apt-get install -y libcudnn9-cuda-12 libcudnn9-dev-cuda-12 \
    && rm cudnn-local-repo-ubuntu2204-9.0.0_1.0-1_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY utils/ ./utils/
COPY llm/ ./llm/
COPY flow/ ./flow/
COPY cosyvoice/ ./cosyvoice/
COPY ckpt/ ./ckpt/
COPY frontend/ ./frontend/
COPY configs/ ./configs/
COPY static/ ./static/
COPY templates/ ./templates/

# Download models - All-in-One
RUN mkdir -p /app/ckpt && \
    mkdir -p /app/examples && \
    cd /app && \
    git clone --depth=1 https://www.modelscope.cn/iic/CosyVoice-300M.git ckpt/CosyVoice-300M && \
    git clone --depth=1 https://www.modelscope.cn/ZhipuAI/glm-4-voice-9b.git ckpt/glm-4-voice-9b

# Create temp directory
RUN mkdir -p /tmp/glm-tts-voices

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run FastAPI server
CMD ["python3", "fastapi_server.py"]
