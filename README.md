[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# GLM-TTS Enhanced: Production-Ready TTS Service

[![Docker Hub](https://img.shields.io/docker/v/neosun/glm-tts?label=Docker%20Hub)](https://hub.docker.com/r/neosun/glm-tts)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://www.python.org/)

Enhanced version of GLM-TTS with production-ready features: Web UI, REST API, Whisper auto-transcription, and Docker deployment.

![GLM-TTS Enhanced UI](https://img.aws.xin/uPic/kMHzYn.png)

## ✨ Enhanced Features

### 🎯 Core Enhancements
- **🌐 Modern Web UI**: Responsive interface with real-time progress tracking
- **🔌 REST API**: Complete API with Swagger documentation at `/apidocs`
- **🎤 Whisper Integration**: Automatic audio transcription when reference text is empty
- **📊 Real-time Progress**: SSE-based streaming with elapsed time display
- **🐳 All-in-One Docker**: 23.6GB image with all models and dependencies
- **⚡ GPU Optimized**: cuDNN 9 support for ONNX Runtime GPU acceleration
- **💾 Persistent Storage**: Host-mounted directory for file management
- **🔧 Advanced Controls**: Temperature, Top-p, and sampling strategy parameters
- **🤖 MCP Server**: Model Context Protocol server for AI agent integration

### 🆕 What's New
- Whisper auto-transcription (leave reference text empty)
- Real-time generation progress with timing
- Experimental advanced parameters
- Files stored on host at `/tmp/glm-tts-voices`
- Full ONNX Runtime GPU acceleration with cuDNN 9
- MCP server for seamless AI agent integration

## 🚀 Quick Start (Recommended)

### Using Docker (All-in-One Image)

```bash
# Pull the latest v2.3.1 image
docker pull neosun/glm-tts:all-in-one-fastapi-v2.3.1

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
  neosun/glm-tts:all-in-one-fastapi-v2.3.1
```

**Access the Web UI**: `http://localhost:8080`

### Using Docker Compose

```yaml
version: '3.8'

services:
  glm-tts:
    image: neosun/glm-tts:all-in-one
    container_name: glm-tts
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
      - PORT=8080
      - TEMP_DIR=/tmp/glm-tts-voices
    ports:
      - "8080:8080"
    volumes:
      - /tmp/glm-tts-voices:/tmp/glm-tts-voices
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
```

Start the service:
```bash
docker-compose up -d
```

## 📖 Usage

### Web Interface

1. Open `http://localhost:8080` in your browser
2. Upload a reference audio file (3-10 seconds, WAV format)
3. Enter text to synthesize
4. **Optional**: Leave "Reference Text" empty for auto-transcription via Whisper
5. **Optional**: Expand "Advanced Parameters" for fine-tuning
6. Click "Generate Speech" and watch real-time progress
7. Download the generated audio

### REST API

**Generate Speech:**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=Hello, this is a test." \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=Reference audio text" \
  -F "temperature=0.8" \
  -F "top_p=0.9" \
  -F "sampling_strategy=balanced"
```

**API Documentation**: Visit `http://localhost:8080/apidocs` for interactive Swagger docs.

**Health Check:**
```bash
curl http://localhost:8080/health
```

### MCP Server Integration

The project includes an MCP (Model Context Protocol) server for AI agent integration:

```bash
# Start MCP server
python mcp_server.py

# Configure in your AI agent (e.g., Claude Desktop)
# See MCP_GUIDE.md for detailed setup
```

### Advanced Parameters

- **Temperature** (0.1-1.5): Controls randomness (higher = more varied)
- **Top-p** (0.5-1.0): Nucleus sampling threshold
- **Sampling Strategy**:
  - `fast`: Quick generation, lower quality
  - `balanced`: Default, good quality/speed trade-off
  - `quality`: Best quality, slower generation
- **Skip Whisper**: Disable auto-transcription for faster processing

## 🏗️ Architecture

```
┌─────────────────┐
│   Web UI        │
│  (HTML/JS)      │
└────────┬────────┘
         │
┌────────▼────────┐
│ FastAPI Server  │
│(fastapi_server) │
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

### Enhanced Components

| Component | Description |
|-----------|-------------|
| `fastapi_server.py` | FastAPI REST API with SSE streaming support |
| `tts_engine.py` | TTS inference engine with Whisper integration |
| `mcp_server.py` | MCP server for AI agent integration |
| `Dockerfile` | Multi-stage build with cuDNN 9 |
| `docker-compose.yml` | Production deployment configuration |

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

```bash
docker run -e NVIDIA_VISIBLE_DEVICES=2 ...
```

Or in `docker-compose.yml`:
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

- **Model Size**: 23.6GB (all-in-one image with v2.3.1)
- **VRAM Usage**: ~12GB during inference
- **Generation Speed**: 2-3 seconds for 10-second audio (20-30x faster than v2.0.0)
- **Whisper Overhead**: +2-3 seconds for auto-transcription
- **Startup Time**: ~90 seconds (one-time model loading)
- **Models Cached**: All models resident in GPU memory for instant inference

## 🛠️ Troubleshooting

### Common Issues

**CUDA Out of Memory**
- Use a GPU with more VRAM (16GB+ recommended)
- Close other GPU applications

**cuDNN Version Mismatch**
- Use the provided Docker image (cuDNN 9 included)
- Check: `ldconfig -p | grep cudnn`

**Slow Generation**
- Verify GPU usage: `nvidia-smi`
- Check NVIDIA_VISIBLE_DEVICES matches your GPU

**Whisper Fails**
- Ensure audio is clear and in supported format
- Use `skip_whisper=true` to bypass

## 📦 Building from Source

```bash
# Build Docker image
docker build -t glm-tts:custom .

# Push to registry
docker tag glm-tts:custom your-registry/glm-tts:latest
docker push your-registry/glm-tts:latest
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 Changelog

### v2.3.1 (2025-12-13)
- ⚡ **20-30x Performance Boost**: Inference time reduced from 60s to 2-3s
- 🏗️ Architecture Overhaul: Direct model loading in TTSEngine, eliminated subprocess overhead
- 💾 Models Resident in GPU Memory: All models (Whisper, LLM, Flow) pre-loaded and cached
- 🔧 Fixed Flow Model Wrapper: Proper Token2Wav integration for token2wav_with_cache
- 🎤 Enhanced Whisper Integration: Auto-transcription with skip_whisper parameter support
- ✅ Full API Test Coverage: All 10 API endpoints validated (standard TTS, streaming, voice_id, upload)
- 🚀 Production Ready: Stable performance with consistent 2-3s generation time

### v2.0.0 (2025-12-12)
- 🚀 Streaming TTS with SSE (Server-Sent Events)
- ⚡ Pre-generation architecture for async optimization
- 🎵 Real-time audio chunk delivery
- 🔄 FastAPI framework migration
- 📡 Standard and streaming TTS dual modes
- 🎯 Production-ready streaming pipeline

### v1.0.0 (2025-12-12)
- ✨ Initial enhanced release
- 🌐 Web UI with real-time progress
- 🔌 REST API with Swagger docs
- 🎤 Whisper auto-transcription
- 🐳 All-in-one Docker image (20.5GB)
- ⚡ cuDNN 9 for ONNX Runtime
- 💾 Host-mounted storage
- 🔧 Advanced parameter controls
- 🤖 MCP server integration

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE)

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
