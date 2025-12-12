# GLM-TTS Enhancement Summary

## 项目概述

本项目是 [GLM-TTS](https://github.com/zai-org/GLM-TTS) 的增强版本，添加了生产级功能，使其可以直接部署到生产环境。

## 核心增强功能

### 1. Web 用户界面 (server.py)
- **现代化 UI**: 响应式设计，支持移动端
- **实时进度**: SSE (Server-Sent Events) 推送生成进度
- **计时功能**: 显示生成耗时
- **文件管理**: 上传、生成、下载一体化
- **高级参数**: 可折叠的实验性参数面板

### 2. TTS 推理引擎 (tts_engine.py)
- **Whisper 集成**: 自动音频转录功能
- **进度回调**: 支持实时进度更新
- **参数控制**: Temperature, Top-p, 采样策略
- **错误处理**: 完善的异常处理机制
- **GPU 优化**: 延迟加载 Whisper 模型

### 3. Docker 部署 (Dockerfile + docker-compose.yml)
- **All-in-One 镜像**: 20.5GB 包含所有依赖和模型
- **cuDNN 9 支持**: 完整的 ONNX Runtime GPU 加速
- **GPU 映射**: 正确的设备 ID 配置
- **健康检查**: 自动重启和健康监控
- **持久化存储**: 挂载宿主机目录

### 4. REST API
- **Swagger 文档**: 交互式 API 文档
- **CORS 支持**: 跨域请求支持
- **文件上传**: 支持音频文件上传
- **进度流**: SSE 实时进度推送
- **错误处理**: 统一的错误响应格式

## 技术栈

### 后端
- **Flask**: Web 框架
- **PyTorch**: 深度学习框架
- **ONNX Runtime**: GPU 推理加速
- **Whisper**: 音频转录
- **Flasgger**: Swagger 文档生成

### 前端
- **原生 HTML/CSS/JS**: 无框架依赖
- **EventSource API**: SSE 客户端
- **Fetch API**: 异步请求

### 部署
- **Docker**: 容器化
- **NVIDIA Container Runtime**: GPU 支持
- **Nginx**: 反向代理（可选）

## 文件结构

```
GLM-TTS-Enhanced/
├── server.py                 # Flask API 服务器
├── tts_engine.py            # TTS 推理引擎
├── Dockerfile               # Docker 镜像构建
├── docker-compose.yml       # Docker Compose 配置
├── requirements.txt         # Python 依赖
├── start.sh                 # 启动脚本
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略规则
├── DEPLOY.md               # 部署文档
├── README_ENHANCE.md       # 英文文档
├── README_ENHANCE_CN.md    # 简体中文文档
├── README_ENHANCE_TW.md    # 繁体中文文档
├── README_ENHANCE_JP.md    # 日文文档
└── SECURITY_REPORT.md      # 安全检查报告
```

## 关键改进

### 1. Whisper 自动转录
**问题**: 用户需要手动输入参考音频的文本内容  
**解决**: 集成 Whisper 模型，参考文本留空时自动识别

```python
if not prompt_text or prompt_text.strip() == "":
    if not skip_whisper:
        prompt_text = self.transcribe_audio(prompt_audio_path)
```

### 2. 实时进度显示
**问题**: 生成过程无反馈，用户不知道进度  
**解决**: 使用 SSE 推送实时进度和计时信息

```python
@app.route('/api/tts/progress/<task_id>')
def tts_progress(task_id):
    def generate():
        while True:
            if task_id in progress_store:
                progress = progress_store[task_id]
                yield f"data: {jsonify(progress).get_data(as_text=True)}\n\n"
```

### 3. GPU 设备映射
**问题**: Docker 容器使用错误的 GPU  
**解决**: 硬编码 device_ids 确保使用正确的 GPU

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['2']  # 指定 GPU ID
          capabilities: [gpu]
```

### 4. cuDNN 9 支持
**问题**: ONNX Runtime 需要 cuDNN 9，原镜像只有 cuDNN 8  
**解决**: 在 Dockerfile 中安装 cuDNN 9

```dockerfile
RUN apt-get update && \
    apt-get install -y libcudnn9-cuda-12 libcudnn9-dev-cuda-12
```

### 5. 持久化存储
**问题**: 容器内文件重启后丢失  
**解决**: 挂载宿主机目录

```yaml
volumes:
  - /tmp/glm-tts-voices:/tmp/glm-tts-voices
```

## 性能指标

| 指标 | 数值 |
|------|------|
| 镜像大小 | 20.5GB |
| 显存占用 | ~12GB |
| 生成速度 | 2-5秒/10秒音频 |
| Whisper 开销 | +2-3秒 |
| 启动时间 | ~30秒 |

## 部署方式

### 方式一：Docker Run
```bash
docker run -d --name glm-tts --runtime=nvidia \
  -e NVIDIA_VISIBLE_DEVICES=0 \
  -p 8080:8080 \
  -v /tmp/glm-tts-voices:/tmp/glm-tts-voices \
  neosun/glm-tts:all-in-one
```

### 方式二：Docker Compose
```bash
docker-compose up -d
```

### 方式三：手动安装
```bash
pip install -r requirements.txt
python server.py
```

## API 使用示例

### 生成语音
```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=你好，这是一个测试。" \
  -F "prompt_audio=@reference.wav" \
  -F "temperature=0.8"
```

### 查看进度
```javascript
const eventSource = new EventSource(`/api/tts/progress/${taskId}`);
eventSource.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(progress.message, progress.elapsed);
};
```

## 高级参数说明

| 参数 | 范围 | 默认值 | 说明 |
|------|------|--------|------|
| temperature | 0.1-1.5 | 0.8 | 控制随机性 |
| top_p | 0.5-1.0 | 0.9 | 核采样阈值 |
| sampling_strategy | fast/balanced/quality | balanced | 采样策略 |
| skip_whisper | true/false | false | 跳过自动转录 |

## 已知限制

1. **Temperature/Top-p**: 当前仅 UI 展示，需修改 glmtts_inference.py 才能生效
2. **模型大小**: 20.5GB 镜像较大，首次拉取需要时间
3. **显存需求**: 至少需要 16GB 显存
4. **并发限制**: 单 GPU 同时只能处理一个请求

## 未来改进

- [ ] 实现 Temperature/Top-p 参数实际生效
- [ ] 添加批量处理支持
- [ ] 实现请求队列管理
- [ ] 添加用户认证
- [ ] 支持更多音频格式
- [ ] 添加音频预处理功能
- [ ] 实现模型热更新
- [ ] 添加监控和日志系统

## 贡献者

- **neosun100** - 项目维护者
- **GLM-TTS Team** - 原始模型开发

## 许可证

Apache License 2.0

## 相关链接

- **GitHub**: https://github.com/neosun100/GLM-TTS-Enhanced
- **Docker Hub**: https://hub.docker.com/r/neosun/glm-tts
- **原始项目**: https://github.com/zai-org/GLM-TTS
- **在线演示**: https://glm-tts.aws.xin

---

**最后更新**: 2025-12-12  
**版本**: v1.0.0
