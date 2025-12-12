# GLM-TTS 快速开始 ⚡

## 一分钟启动

```bash
# 1. 下载模型（首次运行）
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt

# 2. 启动服务
./start.sh

# 3. 访问
# UI: http://0.0.0.0:8080
# API: http://0.0.0.0:8080/docs
```

## 三种使用方式

### 🖥️ UI 界面
```
打开浏览器 → http://0.0.0.0:8080
上传音频 → 输入文本 → 生成
```

### 🔌 API 调用
```bash
curl -X POST http://0.0.0.0:8080/api/tts \
  -F "text=你好" \
  -F "prompt_audio=@prompt.wav" \
  -o output.wav
```

### 🤖 MCP 集成
```json
// 添加到 claude_desktop_config.json
{
  "mcpServers": {
    "glm-tts": {
      "command": "python3",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

## 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启
docker-compose restart

# 测试
./test_deployment.sh
```

## GPU 管理

```bash
# 查看状态
curl http://0.0.0.0:8080/api/gpu/status

# 释放显存
curl -X POST http://0.0.0.0:8080/api/gpu/offload
```

## 配置调整

编辑 `.env`:
```bash
PORT=8080              # 修改端口
GPU_IDLE_TIMEOUT=60    # GPU 空闲超时
```

## 问题排查

| 问题 | 解决方案 |
|------|---------|
| 端口占用 | 修改 `.env` 中的 `PORT` |
| GPU 不足 | 调用 `/api/gpu/offload` |
| 模型缺失 | 重新下载到 `ckpt/` |
| 容器失败 | 检查 `docker-compose logs` |

## 文档索引

- 📖 [完整文档](DEPLOYMENT.md)
- 🐳 [Docker 指南](README_DOCKER.md)
- 🤖 [MCP 指南](MCP_GUIDE.md)
- 📚 [项目主页](README.md)
