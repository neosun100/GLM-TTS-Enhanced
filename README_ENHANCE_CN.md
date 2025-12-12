[English](README_ENHANCE.md) | [简体中文](README_ENHANCE_CN.md) | [繁體中文](README_ENHANCE_TW.md) | [日本語](README_ENHANCE_JP.md)

# GLM-TTS 增强版：生产级 TTS 服务与 Web 界面

[![Docker Hub](https://img.shields.io/docker/v/neosun/glm-tts?label=Docker%20Hub)](https://hub.docker.com/r/neosun/glm-tts)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://www.python.org/)

[GLM-TTS](https://github.com/zai-org/GLM-TTS) 的增强版本，提供生产级功能，包括 Web UI、REST API、自动转录和 Docker 部署。

## ✨ 增强功能

### 🎯 核心增强
- **🌐 Web 界面**：现代化响应式界面，实时进度跟踪
- **🔌 REST API**：完整的 API 与 Swagger 文档
- **🎤 自动转录**：集成 Whisper 自动生成参考文本
- **📊 实时进度**：基于 SSE 的进度流式传输与计时信息
- **🐳 Docker 就绪**：预装所有依赖的一体化 Docker 镜像
- **⚡ GPU 优化**：正确的 GPU 设备映射和 cuDNN 9 支持
- **💾 持久化存储**：挂载宿主机目录进行文件管理
- **🔧 高级控制**：Temperature、Top-p 和采样策略参数

### 🆕 新增特性
- **Whisper 自动转录**：参考文本留空时自动从音频识别
- **进度跟踪**：实时生成进度与耗时显示
- **高级参数**：实验性控制用于微调输出质量
- **改进存储**：文件存储在宿主机 `/tmp/glm-tts-voices`
- **cuDNN 9 支持**：完整的 ONNX Runtime GPU 加速
- **一体化镜像**：20.5GB Docker 镜像包含所有模型

## 🚀 快速开始

### 方式一：Docker（推荐）

拉取并运行一体化镜像：

```bash
# 拉取镜像
docker pull neosun/glm-tts:all-in-one

# 创建临时目录
mkdir -p /tmp/glm-tts-voices
chmod 777 /tmp/glm-tts-voices

# 使用 GPU 0 运行（根据需要更改设备 ID）
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

访问 Web 界面：`http://localhost:8080`

### 方式二：Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  glm-tts:
    image: neosun/glm-tts:all-in-one
    container_name: glm-tts
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0  # 在此更改 GPU ID
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
              device_ids: ['0']  # 在此更改 GPU ID
              capabilities: [gpu]
```

启动服务：

```bash
docker-compose up -d
```

### 方式三：手动安装

**前置要求：**
- Python 3.10 - 3.12
- CUDA 12.1+
- cuDNN 9
- NVIDIA GPU 16GB+ 显存

**安装步骤：**

```bash
# 克隆仓库
git clone https://github.com/neosun100/GLM-TTS-Enhanced.git
cd GLM-TTS-Enhanced

# 安装依赖
pip install -r requirements.txt
pip install flask flasgger flask-cors onnxruntime-gpu openai-whisper

# 下载模型
mkdir -p ckpt
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt

# 启动服务器
python server.py
```

## 📖 使用方法

### Web 界面

1. 在浏览器中打开 `http://localhost:8080`
2. 上传参考音频文件（3-10 秒）
3. 输入要合成的文本（或留空参考文本以自动转录）
4. 点击"生成语音"并观察实时进度
5. 下载生成的音频

### REST API

**生成语音：**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=你好，这是一个测试。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参考音频的文本内容" \
  -F "temperature=0.8" \
  -F "top_p=0.9" \
  -F "sampling_strategy=balanced"
```

**API 文档：**

访问 `http://localhost:8080/apidocs` 查看交互式 Swagger 文档。

### 高级参数

- **Temperature** (0.1-1.5)：控制随机性（越高越多样化）
- **Top-p** (0.5-1.0)：核采样阈值
- **采样策略**：
  - `fast`：快速生成，质量较低
  - `balanced`：默认，质量/速度平衡
  - `quality`：最佳质量，生成较慢
- **跳过 Whisper**：禁用自动转录以加快处理速度

## 🏗️ 架构

### 系统组件

```
┌─────────────────┐
│   Web UI        │
│  (HTML/JS)      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Flask 服务器   │
│  (server.py)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  TTS 引擎       │
│ (tts_engine.py) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Whisper│  │GLM-TTS│
│ 模型  │  │ 模型  │
└───────┘  └───────┘
```

### 增强文件

| 文件 | 用途 |
|------|------|
| `server.py` | Flask REST API 与 SSE 进度流 |
| `tts_engine.py` | TTS 推理引擎与 Whisper 集成 |
| `Dockerfile` | 多阶段构建与 cuDNN 9 |
| `docker-compose.yml` | 生产部署配置 |
| `.gitignore` | 增强以排除敏感数据 |

## 🔧 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | 8080 | 服务器端口 |
| `TEMP_DIR` | `/tmp/glm-tts-voices` | 临时文件存储 |
| `GPU_IDLE_TIMEOUT` | 60 | GPU 空闲超时（秒） |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU 设备 ID |

### GPU 选择

使用特定 GPU（例如 GPU 2）：

**Docker Run：**
```bash
docker run -e NVIDIA_VISIBLE_DEVICES=2 ...
```

**Docker Compose：**
```yaml
environment:
  - NVIDIA_VISIBLE_DEVICES=2
deploy:
  resources:
    reservations:
      devices:
        - device_ids: ['2']
```

## 📊 性能

- **模型大小**：20.5GB（一体化镜像）
- **显存使用**：推理时约 12GB
- **生成速度**：10 秒音频需 2-5 秒
- **Whisper 开销**：自动转录增加 2-3 秒

## 🛠️ 故障排除

### 常见问题

**1. CUDA 内存不足**
- 减少批量大小或使用更大显存的 GPU
- 关闭其他 GPU 密集型应用

**2. cuDNN 版本不匹配**
- 确保安装 cuDNN 9（Docker 镜像已包含）
- 检查：`ldconfig -p | grep cudnn`

**3. 生成缓慢**
- 验证正在使用 GPU：`nvidia-smi`
- 检查 NVIDIA_VISIBLE_DEVICES 是否匹配您的 GPU

**4. Whisper 失败**
- 确保音频清晰且格式受支持
- 使用 `skip_whisper=true` 绕过自动转录

## 📦 从源码构建

```bash
# 构建 Docker 镜像
docker build -t glm-tts:custom .

# 推送到仓库
docker tag glm-tts:custom your-registry/glm-tts:latest
docker push your-registry/glm-tts:latest
```

## 🤝 贡献

欢迎贡献！请：

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 打开 Pull Request

## 📝 更新日志

### v1.0.0 (2025-12-12)
- ✨ 初始增强版本发布
- 🌐 添加实时进度的 Web UI
- 🔌 REST API 与 Swagger 文档
- 🎤 Whisper 自动转录集成
- 🐳 一体化 Docker 镜像（20.5GB）
- ⚡ ONNX Runtime 的 cuDNN 9 支持
- 💾 宿主机挂载存储以实现持久化
- 🔧 高级参数控制

## 📄 许可证

本项目采用 Apache License 2.0 许可 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [GLM-TTS](https://github.com/zai-org/GLM-TTS) - 原始 TTS 模型
- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) - 前端框架

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/GLM-TTS-Enhanced&type=Date)](https://star-history.com/#neosun100/GLM-TTS-Enhanced)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**由 GLM-TTS 增强团队用 ❤️ 制作**
