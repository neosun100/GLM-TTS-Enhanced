[English](README_ENHANCE.md) | [简体中文](README_ENHANCE_CN.md) | [繁體中文](README_ENHANCE_TW.md) | [日本語](README_ENHANCE_JP.md)

# GLM-TTS Enhanced: Production-Ready TTS Service with Web UI

[![Docker Hub](https://img.shields.io/docker/v/neosun/glm-tts?label=Docker%20Hub)](https://hub.docker.com/r/neosun/glm-tts)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://www.python.org/)

Enhanced version of [GLM-TTS](https://github.com/zai-org/GLM-TTS) with production-ready features including web UI, REST API, automatic transcription, and Docker deployment.

## ✨ Enhanced Features

### 🎯 Core Enhancements
- **🌐 Web UI**: Modern, responsive interface with real-time progress tracking
- **🔌 REST API**: Complete API with Swagger documentation
- **🎤 Auto Transcription**: Whisper integration for automatic reference text generation
- **📊 Real-time Progress**: SSE-based progress streaming with timing information
- **🐳 Docker Ready**: All-in-one Docker image with all dependencies pre-installed
- **⚡ GPU Optimization**: Proper GPU device mapping and cuDNN 9 support
- **💾 Persistent Storage**: Host-mounted temporary directory for file management
- **🔧 Advanced Controls**: Temperature, Top-p, and sampling strategy parameters

### 🆕 What's New
- **Whisper Auto-Transcription**: Leave reference text empty to auto-detect from audio
- **Progress Tracking**: Real-time generation progress with elapsed time display
- **Advanced Parameters**: Experimental controls for fine-tuning output quality
- **Improved Storage**: Files stored on host machine at `/tmp/glm-tts-voices`
- **cuDNN 9 Support**: Full ONNX Runtime GPU acceleration
- **All-in-One Image**: 20.5GB Docker image with all models included

## 🚀 Quick Start

### Option 1: Docker (Recommended)

Pull and run the all-in-one image:

```bash
# Pull the image
docker pull neosun/glm-tts:all-in-one

# Create temporary directory
mkdir -p /tmp/glm-tts-voices
chmod 777 /tmp/glm-tts-voices

# Run with GPU 0 (change device ID as needed)
docker run -d \
  --name glm-tts \
  --runtime=nvidia \
  -e NVIDIA_VISIBLE_DEVICES=0 \
  -e PORT=8080 \
  -e TEMP_DIR=/tmp/glm-tts-voices \
  -p 8080:8080 \
  -v /tmp/glm-tts-voices:/tmp/glm-tts-voices \
  --restart unless-stopped \
  neosun/glm-tts:all-in-one
```

Access the web UI at: `http://localhost:8080`

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  glm-tts:
    image: neosun/glm-tts:all-in-one
    container_name: glm-tts
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0  # Change GPU ID here
      - PORT=8080
      - GPU_IDLE_TIMEOUT=60
      - TEMP_DIR=/tmp/glm-tts-voices
    ports:
      - "8080:8080"
    volumes:
      - /tmp/glm-tts-voices:/tmp/glm-tts-voices
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']  # Change GPU ID here
              capabilities: [gpu]
```

Start the service:

```bash
docker-compose up -d
```

### Option 3: Manual Installation

**Prerequisites:**
- Python 3.10 - 3.12
- CUDA 12.1+
- cuDNN 9
- NVIDIA GPU with 16GB+ VRAM

**Installation:**

```bash
# Clone repository
git clone https://github.com/neosun100/GLM-TTS-Enhanced.git
cd GLM-TTS-Enhanced

# Install dependencies
pip install -r requirements.txt
pip install flask flasgger flask-cors onnxruntime-gpu openai-whisper

# Download models
mkdir -p ckpt
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt

# Start server
python server.py
```

## 📖 Usage

### Web Interface

1. Open `http://localhost:8080` in your browser
2. Upload a reference audio file (3-10 seconds)
3. Enter text to synthesize (or leave reference text empty for auto-transcription)
4. Click "Generate Speech" and watch real-time progress
5. Download the generated audio

### REST API

**Generate Speech:**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=你好，这是一个测试。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参考音频的文本内容" \
  -F "temperature=0.8" \
  -F "top_p=0.9" \
  -F "sampling_strategy=balanced"
```

**API Documentation:**

Visit `http://localhost:8080/apidocs` for interactive Swagger documentation.

### Advanced Parameters

- **Temperature** (0.1-1.5): Controls randomness (higher = more varied)
- **Top-p** (0.5-1.0): Nucleus sampling threshold
- **Sampling Strategy**: 
  - `fast`: Quick generation, lower quality
  - `balanced`: Default, good quality/speed trade-off
  - `quality`: Best quality, slower generation
- **Skip Whisper**: Disable auto-transcription for faster processing

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│   Web UI        │
│  (HTML/JS)      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Flask Server   │
│  (server.py)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  TTS Engine     │
│ (tts_engine.py) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Whisper│  │GLM-TTS│
│ Model │  │ Model │
└───────┘  └───────┘
```

### Enhanced Files

| File | Purpose |
|------|---------|
| `server.py` | Flask REST API with SSE progress streaming |
| `tts_engine.py` | TTS inference engine with Whisper integration |
| `Dockerfile` | Multi-stage build with cuDNN 9 |
| `docker-compose.yml` | Production deployment configuration |
| `.gitignore` | Enhanced to exclude sensitive data |

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8080 | Server port |
| `TEMP_DIR` | `/tmp/glm-tts-voices` | Temporary file storage |
| `GPU_IDLE_TIMEOUT` | 60 | GPU idle timeout (seconds) |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU device ID |

### GPU Selection

To use a specific GPU (e.g., GPU 2):

**Docker Run:**
```bash
docker run -e NVIDIA_VISIBLE_DEVICES=2 ...
```

**Docker Compose:**
```yaml
environment:
  - NVIDIA_VISIBLE_DEVICES=2
deploy:
  resources:
    reservations:
      devices:
        - device_ids: ['2']
```

## 📊 Performance

- **Model Size**: 20.5GB (all-in-one image)
- **VRAM Usage**: ~12GB during inference
- **Generation Speed**: 2-5 seconds for 10-second audio
- **Whisper Overhead**: +2-3 seconds for auto-transcription

## 🛠️ Troubleshooting

### Common Issues

**1. CUDA Out of Memory**
- Reduce batch size or use a GPU with more VRAM
- Close other GPU-intensive applications

**2. cuDNN Version Mismatch**
- Ensure cuDNN 9 is installed (included in Docker image)
- Check: `ldconfig -p | grep cudnn`

**3. Slow Generation**
- Verify GPU is being used: `nvidia-smi`
- Check NVIDIA_VISIBLE_DEVICES matches your GPU

**4. Whisper Fails**
- Ensure audio is clear and in supported format
- Use `skip_whisper=true` to bypass auto-transcription

## 📦 Building from Source

```bash
# Build Docker image
docker build -t glm-tts:custom .

# Push to registry
docker tag glm-tts:custom your-registry/glm-tts:latest
docker push your-registry/glm-tts:latest
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 Changelog

### v1.0.0 (2025-12-12)
- ✨ Initial enhanced release
- 🌐 Added web UI with real-time progress
- 🔌 REST API with Swagger documentation
- 🎤 Whisper auto-transcription integration
- 🐳 All-in-one Docker image (20.5GB)
- ⚡ cuDNN 9 support for ONNX Runtime
- 💾 Host-mounted storage for persistence
- 🔧 Advanced parameter controls

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [GLM-TTS](https://github.com/zai-org/GLM-TTS) - Original TTS model
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) - Frontend framework

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/GLM-TTS-Enhanced&type=Date)](https://star-history.com/#neosun100/GLM-TTS-Enhanced)

## 📱 Follow Us

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**Made with ❤️ by the GLM-TTS Enhanced Team**
