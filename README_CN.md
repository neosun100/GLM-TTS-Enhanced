[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# GLM-TTS 增强版：生产级 TTS 服务

[![Docker Hub](https://img.shields.io/docker/v/neosun/glm-tts?label=Docker%20Hub)](https://hub.docker.com/r/neosun/glm-tts)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://www.python.org/)

GLM-TTS 的增强版本，提供生产级功能：Web UI、REST API、Whisper 自动转录和 Docker 部署。

![GLM-TTS Enhanced UI](https://img.aws.xin/uPic/YD5e2C.png)

## ✨ 增强功能

### 🎯 核心增强
- **🌐 现代化 Web 界面**：响应式界面，实时进度跟踪
- **🔌 REST API**：完整的 API，Swagger 文档位于 `/apidocs`
- **🎤 Whisper 集成**：参考文本为空时自动音频转录
- **📊 实时进度**：基于 SSE 的流式传输，显示耗时
- **🐳 一体化 Docker**：23.6GB 镜像包含所有模型和依赖
- **⚡ GPU 优化**：cuDNN 9 支持 ONNX Runtime GPU 加速
- **💾 持久化存储**：挂载宿主机目录进行文件管理
- **🔧 高级控制**：Temperature、Top-p 和采样策略参数
- **🤖 MCP 服务器**：Model Context Protocol 服务器用于 AI 代理集成

### 🆕 新增特性
- Whisper 自动转录（参考文本留空即可）
- 实时生成进度与计时
- 实验性高级参数
- 文件存储在宿主机 `/tmp/glm-tts-voices`
- 完整的 ONNX Runtime GPU 加速（cuDNN 9）
- MCP 服务器无缝集成 AI 代理

## 🚀 快速开始（推荐）

### 使用 Docker（一体化镜像）

```bash
# 拉取最新 v2.3.1 镜像
docker pull neosun/glm-tts:all-in-one-fastapi-v2.3.1

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
  neosun/glm-tts:all-in-one-fastapi-v2.3.1
```

**访问 Web 界面**：`http://localhost:8080`

### 使用 Docker Compose

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

启动服务：
```bash
docker-compose up -d
```

## 📖 使用方法

### Web 界面

1. 在浏览器中打开 `http://localhost:8080`
2. 上传参考音频文件（3-10 秒，WAV 格式）
3. 输入要合成的文本
4. **可选**：参考文本留空，通过 Whisper 自动转录
5. **可选**：展开"高级参数"进行微调
6. 点击"生成语音"并观察实时进度
7. 下载生成的音频

### REST API

**生成语音：**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=你好，这是一个测试。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参考音频文本" \
  -F "temperature=0.8" \
  -F "top_p=0.9" \
  -F "sampling_strategy=balanced"
```

**API 文档**：访问 `http://localhost:8080/apidocs` 查看交互式 Swagger 文档。

**健康检查：**
```bash
curl http://localhost:8080/health
```

### MCP 服务器集成

项目包含 MCP（Model Context Protocol）服务器用于 AI 代理集成：

```bash
# 启动 MCP 服务器
python mcp_server.py

# 在 AI 代理中配置（例如 Claude Desktop）
# 详见 MCP_GUIDE.md
```

### 高级参数

- **Temperature** (0.1-1.5)：控制随机性（越高越多样化）
- **Top-p** (0.5-1.0)：核采样阈值
- **采样策略**：
  - `fast`：快速生成，质量较低
  - `balanced`：默认，质量/速度平衡
  - `quality`：最佳质量，生成较慢
- **跳过 Whisper**：禁用自动转录以加快处理

## 🏗️ 架构

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

### 增强组件

| 组件 | 说明 |
|------|------|
| `server.py` | Flask REST API 与 SSE 进度流 |
| `tts_engine.py` | TTS 推理引擎与 Whisper 集成 |
| `mcp_server.py` | MCP 服务器用于 AI 代理集成 |
| `Dockerfile` | 多阶段构建与 cuDNN 9 |
| `docker-compose.yml` | 生产部署配置 |

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

```bash
docker run -e NVIDIA_VISIBLE_DEVICES=2 ...
```

或在 `docker-compose.yml` 中：
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

- **模型大小**：23.6GB（v2.3.1一体化镜像）
- **显存使用**：推理时约 12GB
- **生成速度**：10秒音频需2-3秒（比v2.0.0快20-30倍）
- **Whisper 开销**：自动转录增加 2-3 秒
- **启动时间**：约90秒（一次性模型加载）
- **模型缓存**：所有模型常驻GPU内存，实现即时推理

## 🛠️ 故障排除

### 常见问题

**CUDA 内存不足**
- 使用更大显存的 GPU（推荐 16GB+）
- 关闭其他 GPU 应用

**cuDNN 版本不匹配**
- 使用提供的 Docker 镜像（已包含 cuDNN 9）
- 检查：`ldconfig -p | grep cudnn`

**生成缓慢**
- 验证 GPU 使用：`nvidia-smi`
- 检查 NVIDIA_VISIBLE_DEVICES 是否匹配您的 GPU

**Whisper 失败**
- 确保音频清晰且格式受支持
- 使用 `skip_whisper=true` 绕过

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

### v2.3.1 (2025-12-13)
- ⚡ **20-30倍性能提升**：推理时间从60秒降至2-3秒
- 🏗️ 架构重构：TTSEngine直接加载模型，消除subprocess开销
- 💾 模型常驻GPU内存：所有模型（Whisper、LLM、Flow）预加载并缓存
- 🔧 修复Flow模型包装：正确集成Token2Wav实现token2wav_with_cache
- 🎤 增强Whisper集成：支持skip_whisper参数的自动转录
- ✅ 完整API测试覆盖：验证所有10个API端点（标准TTS、流式、voice_id、上传）
- 🚀 生产就绪：稳定性能，生成时间稳定在2-3秒

### v2.0.0 (2025-12-12)
- 🚀 SSE流式TTS（服务器推送事件）
- ⚡ 异步优化的预生成架构
- 🎵 实时音频块传输
- 🔄 FastAPI框架迁移
- 📡 标准和流式TTS双模式
- 🎯 生产就绪的流式管道

### v1.0.0 (2025-12-12)
- ✨ 初始增强版本发布
- 🌐 实时进度的 Web UI
- 🔌 REST API 与 Swagger 文档
- 🎤 Whisper 自动转录
- 🐳 一体化 Docker 镜像（20.5GB）
- ⚡ ONNX Runtime 的 cuDNN 9 支持
- 💾 宿主机挂载存储
- 🔧 高级参数控制
- 🤖 MCP 服务器集成

## 📄 许可证

Apache License 2.0 - 详见 [LICENSE](LICENSE)

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
