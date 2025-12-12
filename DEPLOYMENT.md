# GLM-TTS 部署总览

## 📦 已完成的 Docker 化方案

### 文件清单

```
GLM-TTS/
├── Dockerfile                  # Docker 镜像定义
├── docker-compose.yml          # 容器编排配置
├── .env.example                # 环境变量模板
├── start.sh                    # 一键启动脚本 ⭐
├── test_deployment.sh          # 部署测试脚本
├── server.py                   # 主服务器（UI + API）
├── gpu_manager.py              # GPU 资源管理器
├── mcp_server.py               # MCP 服务器
├── mcp_config.json             # MCP 配置文件
├── MCP_GUIDE.md                # MCP 使用指南
└── README_DOCKER.md            # Docker 部署文档
```

## 🚀 快速开始

### 1. 准备工作

```bash
# 确保已下载模型
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt

# 或使用 ModelScope
modelscope download --model ZhipuAI/GLM-TTS --local_dir ckpt
```

### 2. 启动服务

```bash
./start.sh
```

### 3. 访问服务

- **UI**: http://0.0.0.0:8080
- **API 文档**: http://0.0.0.0:8080/docs
- **MCP**: 见 MCP_GUIDE.md

## 🎯 三种访问模式

### 模式一：UI 界面 🖥️

**特性**：
- ✅ 现代化深色主题
- ✅ 中英文双语支持
- ✅ 实时 GPU 状态监控
- ✅ 参数完整可调
- ✅ 在线音频试听
- ✅ 一键释放显存

**适用场景**：
- 快速测试和演示
- 非技术用户使用
- 参数调试

### 模式二：API 接口 🔌

**特性**：
- ✅ RESTful 设计
- ✅ Swagger 文档
- ✅ 支持流式推理
- ✅ 异步处理
- ✅ GPU 自动管理

**适用场景**：
- 程序化调用
- 批量处理
- 系统集成

**示例**：
```bash
curl -X POST http://0.0.0.0:8080/api/tts \
  -F "text=你好世界" \
  -F "prompt_audio=@prompt.wav" \
  --output output.wav
```

### 模式三：MCP 接口 🤖

**特性**：
- ✅ AI 助手原生集成
- ✅ 自然语言调用
- ✅ 共享 GPU 管理
- ✅ 完整类型注解

**适用场景**：
- Claude Desktop 集成
- Cline 编辑器集成
- AI 工作流自动化

**配置**：
```json
{
  "mcpServers": {
    "glm-tts": {
      "command": "python3",
      "args": ["mcp_server.py"]
    }
  }
}
```

## 🎮 GPU 管理

### 自动管理机制

```
┌─────────────────────────────────────┐
│      GPU Manager (单例)              │
│  - 首次调用时加载模型                 │
│  - 空闲 60s 后自动卸载                │
│  - 所有模式共享同一实例               │
└─────────────────────────────────────┘
         ↓              ↓              ↓
    ┌────────┐    ┌────────┐    ┌────────┐
    │   UI   │    │  API   │    │  MCP   │
    └────────┘    └────────┘    └────────┘
```

### 手动控制

**UI 界面**：点击"释放显存"按钮

**API 调用**：
```bash
curl -X POST http://0.0.0.0:8080/api/gpu/offload
```

**MCP 工具**：
```python
await mcp_client.call_tool("offload_gpu", {})
```

## 🔧 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| PORT | 8080 | 服务端口 |
| GPU_IDLE_TIMEOUT | 60 | GPU 空闲超时（秒）|
| NVIDIA_VISIBLE_DEVICES | 自动 | GPU ID |

### GPU 自动选择

启动脚本会自动选择显存占用最少的 GPU：

```bash
GPU_ID=$(nvidia-smi --query-gpu=index,memory.used \
         --format=csv,noheader,nounits | \
         sort -t',' -k2 -n | head -1 | cut -d',' -f1)
```

当前机器 GPU 状态：
- GPU 0: 7460 MB / 46068 MB
- GPU 1: 13747 MB / 46068 MB
- GPU 2: 3 MB / 46068 MB ⭐ (最空闲)
- GPU 3: 3 MB / 46068 MB

## 📊 架构设计

### 单容器三模式

```
┌─────────────────────────────────────────────┐
│           Docker Container                   │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │         Flask Application               │ │
│  │                                         │ │
│  │  ┌──────────┐  ┌──────────┐           │ │
│  │  │    UI    │  │   API    │           │ │
│  │  │  (HTML)  │  │ (REST)   │           │ │
│  │  └──────────┘  └──────────┘           │ │
│  │       ↓              ↓                 │ │
│  │  ┌────────────────────────┐           │ │
│  │  │   GPU Manager          │           │ │
│  │  │  (Shared Instance)     │           │ │
│  │  └────────────────────────┘           │ │
│  │       ↓                                │ │
│  │  ┌────────────────────────┐           │ │
│  │  │   CosyVoice Model      │           │ │
│  │  └────────────────────────┘           │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │      MCP Server (Separate Process)     │ │
│  │  - Shares GPU Manager                  │ │
│  │  - Provides Tools                      │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 优势

1. **资源共享**：所有模式共享 GPU 和模型
2. **统一管理**：单一容器，易于部署
3. **灵活访问**：支持多种使用方式
4. **自动优化**：智能 GPU 管理

## 🧪 测试验证

```bash
./test_deployment.sh
```

测试项目：
- ✅ 健康检查
- ✅ UI 界面访问
- ✅ API 文档访问
- ✅ GPU 状态查询
- ✅ GPU 卸载功能
- ✅ MCP 文件完整性

## 📝 使用示例

### UI 使用

1. 访问 http://0.0.0.0:8080
2. 输入文本："你好，这是一个测试"
3. 上传参考音频（3-10秒 WAV）
4. 可选：输入参考文本
5. 点击"生成语音"
6. 在线试听或下载

### API 使用

```python
import requests

files = {'prompt_audio': open('prompt.wav', 'rb')}
data = {
    'text': '你好，这是一个测试',
    'prompt_text': '参考文本',
    'stream': 'false'
}

response = requests.post(
    'http://0.0.0.0:8080/api/tts',
    files=files,
    data=data
)

with open('output.wav', 'wb') as f:
    f.write(response.content)
```

### MCP 使用

在 Claude Desktop 中：

> "请使用 GLM-TTS 将'你好世界'转换为语音，使用 prompt.wav 作为参考"

Claude 会自动调用 `text_to_speech` 工具。

## 🔍 故障排除

### 常见问题

**Q: 端口被占用**
```bash
# 修改 .env 中的 PORT
PORT=8081 ./start.sh
```

**Q: GPU 内存不足**
```bash
# 手动释放
curl -X POST http://0.0.0.0:8080/api/gpu/offload
```

**Q: 模型加载失败**
```bash
# 检查模型文件
ls -lh ckpt/
```

**Q: MCP 连接失败**
```bash
# 检查 Python 环境
python3 mcp_server.py
```

## 📚 相关文档

- [README.md](README.md) - 项目主文档
- [README_DOCKER.md](README_DOCKER.md) - Docker 详细说明
- [MCP_GUIDE.md](MCP_GUIDE.md) - MCP 使用指南

## 🎉 完成清单

- [x] Dockerfile 创建
- [x] docker-compose.yml 配置
- [x] 环境变量配置
- [x] 一键启动脚本
- [x] GPU 自动选择
- [x] GPU 资源管理器
- [x] UI 界面（深色主题 + 多语言）
- [x] RESTful API
- [x] Swagger 文档
- [x] MCP 服务器
- [x] MCP 配置文件
- [x] 测试脚本
- [x] 完整文档

## 🚀 下一步

1. 运行 `./start.sh` 启动服务
2. 运行 `./test_deployment.sh` 验证部署
3. 访问 UI 界面测试功能
4. 查看 API 文档了解接口
5. 配置 MCP 集成到 AI 助手

---

**部署完成！享受 GLM-TTS 的强大功能！** 🎙️
