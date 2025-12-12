# GLM-TTS Enhanced v1.2.0 - All-in-One Docker Image
FROM nvidia/cuda:12.1.0-cudnn9-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY static/ ./static/
COPY templates/ ./templates/

# Download models (if not using volume mount)
RUN mkdir -p /app/ckpt

# Create temp directory
RUN mkdir -p /tmp/glm-tts-voices

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run server
CMD ["python3", "server.py"]
