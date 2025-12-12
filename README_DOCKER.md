# GLM-TTS Docker 部署指南

## 快速开始

### 1. 一键启动

```bash
./start.sh
```

脚本会自动：
- ✅ 检查 nvidia-docker 环境
- ✅ 选择显存占用最少的 GPU
- ✅ 检查端口占用
- ✅ 构建并启动容器

### 2. 访问服务

启动成功后，可通过以下方式访问：

- **UI 界面**: http://0.0.0.0:8080
- **API 文档**: http://0.0.0.0:8080/docs
- **MCP 服务**: 见 [MCP_GUIDE.md](MCP_GUIDE.md)

## 三种访问模式

### 模式一：UI 界面

现代化 Web 界面，支持：
- 🌓 深色模式
- 🌍 多语言（中文/英文）
- 📊 实时 GPU 状态
- 🎛️ 完整参数控制
- 🎵 在线试听

**使用步骤**：
1. 打开 http://0.0.0.0:8080
2. 输入文本
3. 上传参考音频（3-10秒）
4. 可选：输入参考文本
5. 点击"生成语音"

### 模式二：API 接口

RESTful API，支持程序化调用。

**主要端点**：

#### 1. 文本转语音
```bash
curl -X POST http://0.0.0.0:8080/api/tts \
  -F "text=你好，这是一个测试" \
  -F "prompt_audio=@prompt.wav" \
  -F "prompt_text=参考文本" \
  -F "stream=false" \
  --output output.wav
```

#### 2. GPU 状态
```bash
curl http://0.0.0.0:8080/api/gpu/status
```

#### 3. 释放显存
```bash
curl -X POST http://0.0.0.0:8080/api/gpu/offload
```

**Swagger 文档**: http://0.0.0.0:8080/docs

### 模式三：MCP 接口

通过 Model Context Protocol 在 AI 助手中使用。

详见 [MCP_GUIDE.md](MCP_GUIDE.md)

## 配置说明

### 环境变量

编辑 `.env` 文件：

```bash
PORT=8080                    # 服务端口
GPU_IDLE_TIMEOUT=60          # GPU 空闲超时（秒）
NVIDIA_VISIBLE_DEVICES=0     # GPU ID（自动选择）
```

### GPU 管理

系统会自动管理 GPU 资源：
- 首次调用时加载模型
- 空闲 60 秒后自动释放显存
- 可手动释放（UI 按钮或 API）

## 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建
docker-compose up -d --build

# 进入容器
docker-compose exec glm-tts bash
```

## 目录结构

```
GLM-TTS/
├── ckpt/           # 模型权重（需下载）
├── examples/       # 示例数据
├── outputs/        # 输出目录（自动创建）
└── ...
```

## 故障排除

### 端口被占用

修改 `.env` 中的 `PORT` 值。

### GPU 内存不足

1. 点击 UI 界面的"释放显存"按钮
2. 或调用 API: `curl -X POST http://0.0.0.0:8080/api/gpu/offload`
3. 或减小 `GPU_IDLE_TIMEOUT` 值

### 模型未下载

```bash
# 下载模型
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt
# 或
modelscope download --model ZhipuAI/GLM-TTS --local_dir ckpt
```

### 容器无法启动

检查 nvidia-docker：
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## 性能优化

### 1. 调整 GPU 超时

根据使用频率调整：
- 频繁使用：`GPU_IDLE_TIMEOUT=300`（5分钟）
- 偶尔使用：`GPU_IDLE_TIMEOUT=60`（1分钟）

### 2. 使用流式推理

适合长文本：
```bash
curl -X POST http://0.0.0.0:8080/api/tts \
  -F "text=很长的文本..." \
  -F "prompt_audio=@prompt.wav" \
  -F "stream=true"
```

## 安全建议

1. **生产环境**：添加认证机制
2. **防火墙**：限制访问 IP
3. **HTTPS**：使用反向代理（Nginx/Caddy）

## 更新日志

- **2025-12-12**: 初始版本
  - ✅ Docker 化
  - ✅ UI + API + MCP 三模式
  - ✅ 自动 GPU 管理
  - ✅ 多语言支持
