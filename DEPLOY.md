# GLM-TTS All-in-One Docker 部署指南

## 镜像信息
- **镜像名称**: `neosun/glm-tts:all-in-one`
- **镜像大小**: 20.5GB
- **包含内容**: 
  - GLM-TTS完整模型（LLM + Flow + Vocoder）
  - Whisper base模型（自动语音识别）
  - 所有Python依赖（Flask, PyTorch, ONNX Runtime等）
  - Web UI界面
  - cuDNN 9支持（完整GPU加速）

## 快速启动

### 方式1：使用docker-compose（推荐）

```bash
# 创建临时目录
mkdir -p /tmp/glm-tts-voices

# 创建docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  glm-tts:
    image: neosun/glm-tts:all-in-one
    container_name: glm-tts
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=2  # 修改为你的GPU编号
      - PORT=8080
      - TEMP_DIR=/tmp/glm-tts-voices
    ports:
      - "0.0.0.0:8080:8080"
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
              device_ids: ['2']  # 修改为你的GPU编号
              capabilities: [gpu]
EOF

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 方式2：直接使用docker run

```bash
# 创建临时目录
mkdir -p /tmp/glm-tts-voices

# 启动容器
docker run -d \
  --name glm-tts \
  --runtime=nvidia \
  --gpus '"device=2"' \
  -e NVIDIA_VISIBLE_DEVICES=2 \
  -e PORT=8080 \
  -e TEMP_DIR=/tmp/glm-tts-voices \
  -p 0.0.0.0:8080:8080 \
  -v /tmp/glm-tts-voices:/tmp/glm-tts-voices \
  --restart unless-stopped \
  neosun/glm-tts:all-in-one
```

## 访问服务

- **Web UI**: http://your-server-ip:8080
- **API文档**: http://your-server-ip:8080/apidocs
- **健康检查**: http://your-server-ip:8080/health

## 功能特性

### 1. 零样本语音克隆
- 上传3-10秒参考音频
- 输入要合成的文本
- 自动克隆音色并生成语音

### 2. 自动语音识别（Whisper）
- 参考文本可留空
- 自动识别参考音频内容
- 节省手动输入时间

### 3. 高级参数（实验性）
- 采样策略：快速/平衡/高质量
- Temperature：控制创造性
- Top-p：控制采样范围
- 跳过Whisper：手动填写参考文本时可勾选

### 4. GPU加速
- 完整GPU支持（cuDNN 9）
- LLM、Flow、Vocoder、ONNX全部GPU加速
- 生成速度：约50-60秒/句

## 数据隐私

所有上传和生成的音频文件存储在：
- **容器内**: `/tmp/glm-tts-voices/`
- **宿主机**: `/tmp/glm-tts-voices/`

文件不会保留在容器内，重启容器不会丢失数据。

## 性能优化建议

1. **跳过Whisper**：如果知道参考音频内容，手动填写并勾选"跳过Whisper"可节省2-3秒
2. **使用快速模式**：选择"快速模式"采样策略
3. **GPU选择**：使用空闲的GPU以获得最佳性能

## 故障排查

### 检查GPU是否被使用
```bash
# 宿主机查看
nvidia-smi

# 容器内查看
docker exec glm-tts nvidia-smi
```

### 查看日志
```bash
docker logs glm-tts -f
```

### 清理临时文件
```bash
rm -rf /tmp/glm-tts-voices/outputs/*
```

## 更新镜像

```bash
docker pull neosun/glm-tts:all-in-one
docker-compose down
docker-compose up -d
```
