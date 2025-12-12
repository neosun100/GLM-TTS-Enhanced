# GLM-TTS MCP 使用指南

## 什么是 MCP？

Model Context Protocol (MCP) 是一个开放协议，用于标准化应用程序如何向 LLM 提供上下文。通过 MCP，您可以在 AI 助手（如 Claude Desktop、Cline）中直接调用 GLM-TTS 的功能。

## 配置 MCP 服务器

### 1. 在 Claude Desktop 中配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）或相应的配置文件：

```json
{
  "mcpServers": {
    "glm-tts": {
      "command": "python3",
      "args": ["/path/to/GLM-TTS/mcp_server.py"],
      "env": {
        "GPU_IDLE_TIMEOUT": "600"
      }
    }
  }
}
```

### 2. 在 Cline 中配置

将 `mcp_config.json` 的内容添加到 Cline 的 MCP 配置中。

## 可用工具

### 1. text_to_speech

将文本转换为语音。

**参数**：
- `text` (string, 必需): 要合成的文本
- `prompt_audio_path` (string, 必需): 参考音频文件路径
- `output_path` (string, 必需): 输出音频文件路径
- `prompt_text` (string, 可选): 参考音频对应的文本
- `stream` (boolean, 可选): 是否使用流式推理，默认 false

**示例**：
```python
result = await mcp_client.call_tool(
    "text_to_speech",
    {
        "text": "你好，这是一个测试。",
        "prompt_audio_path": "/path/to/prompt.wav",
        "output_path": "/path/to/output.wav",
        "prompt_text": "参考文本",
        "stream": false
    }
)
```

**返回**：
```json
{
  "status": "success",
  "output": "/path/to/output.wav"
}
```

### 2. get_gpu_status

获取当前 GPU 状态。

**参数**：无

**示例**：
```python
status = await mcp_client.call_tool("get_gpu_status", {})
```

**返回**：
```json
{
  "loaded": true,
  "idle_time": 15.3
}
```

### 3. offload_gpu

释放 GPU 显存。

**参数**：无

**示例**：
```python
result = await mcp_client.call_tool("offload_gpu", {})
```

**返回**：
```json
{
  "status": "offloaded"
}
```

## MCP vs API 对比

| 特性 | MCP | API |
|------|-----|-----|
| 使用场景 | AI 助手集成 | 程序化调用 |
| 调用方式 | 通过 AI 助手 | HTTP 请求 |
| 认证 | 无需 | 可选 |
| 文档 | 工具描述 | Swagger |
| 适用于 | 交互式任务 | 自动化流程 |

## 使用示例

### 在 Claude Desktop 中使用

配置完成后，您可以直接在对话中说：

> "请使用 GLM-TTS 将这段文本转换为语音：'你好，世界'，使用 /path/to/prompt.wav 作为参考音频，输出到 /path/to/output.wav"

Claude 会自动调用 `text_to_speech` 工具完成任务。

### 在 Cline 中使用

Cline 会在需要时自动调用相应的工具，您只需描述需求即可。

## 注意事项

1. **GPU 管理**：所有工具共享同一个 GPU 管理器，会自动在空闲时释放显存
2. **文件路径**：确保提供的文件路径可访问
3. **音频格式**：参考音频建议为 16kHz WAV 格式
4. **超时设置**：默认 GPU 空闲 600 秒后自动释放，可通过环境变量调整

## 故障排除

### 工具未显示

1. 检查 MCP 配置文件路径是否正确
2. 确认 Python 环境和依赖已安装
3. 重启 AI 助手应用

### GPU 内存不足

调用 `offload_gpu` 工具手动释放显存。

### 音频质量问题

- 确保参考音频清晰、无噪音
- 参考音频长度建议 3-10 秒
- 尝试提供参考文本以提高质量
