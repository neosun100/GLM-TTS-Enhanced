# GLM-TTS v2.0.0 升级指南

## 🎉 重大更新：完全迁移到FastAPI

v2.0.0版本将整个后端框架从Flask迁移到FastAPI，带来更好的性能和现代化特性。

## ✨ 主要改进

### 1. **统一接口设计**
- 单一端点 `/api/tts` 支持两种模式
- 通过HTTP `Accept` 头自动切换：
  - `Accept: application/json` → 传统模式
  - `Accept: text/event-stream` → 流式模式

### 2. **架构简化**
- **v1.3.0**: Flask (8080) + FastAPI (8081) 双服务
- **v2.0.0**: FastAPI (8080) 单服务

### 3. **性能提升**
- 原生异步支持
- 更好的并发处理
- 更低的内存占用

### 4. **开发体验**
- 自动API文档：`http://localhost:8080/docs`
- 类型检查和验证
- 更清晰的错误信息

## 📦 部署方式

### Docker Compose（推荐）
```bash
# 拉取新版本
docker pull neosun/glm-tts:v2.0.0-fastapi

# 启动服务
docker-compose up -d

# 访问
http://localhost:8080
```

### Docker Run
```bash
docker run -d \
  --name glm-tts \
  --runtime=nvidia \
  -e NVIDIA_VISIBLE_DEVICES=0 \
  -e PORT=8080 \
  -p 8080:8080 \
  -v /tmp/glm-tts-voices:/tmp/glm-tts-voices \
  neosun/glm-tts:v2.0.0-fastapi
```

## 🔄 API变化

### 传统模式（无变化）
```javascript
fetch('/api/tts', {
    method: 'POST',
    body: formData,
    headers: {'Accept': 'application/json'}
})
```

### 流式模式（接口统一）
```javascript
// v1.3.0 旧方式
fetch('http://localhost:8081/api/tts/stream', {...})

// v2.0.0 新方式
fetch('/api/tts', {
    method: 'POST',
    body: formData,
    headers: {'Accept': 'text/event-stream'}  // 关键变化
})
```

## 🚀 新功能

### 1. 自动API文档
访问 `http://localhost:8080/docs` 查看交互式API文档

### 2. 健康检查增强
```bash
curl http://localhost:8080/health
# 返回: {"status":"healthy","framework":"FastAPI","version":"2.0.0"}
```

### 3. 更好的错误处理
- 标准HTTP状态码
- 详细错误信息
- 自动参数验证

## ⚠️ 破坏性变化

### 1. 端口变化
- v1.3.0: Flask (8080) + FastAPI (8081)
- v2.0.0: FastAPI (8080) 单端口

### 2. 流式接口
- 旧: `POST /api/tts/stream`
- 新: `POST /api/tts` + `Accept: text/event-stream`

### 3. 依赖变化
- 移除: Flask, Flask-CORS
- 新增: FastAPI, Uvicorn

## 📊 性能对比

| 指标 | v1.3.0 (Flask) | v2.0.0 (FastAPI) | 提升 |
|------|----------------|------------------|------|
| 启动时间 | ~35s | ~30s | 14% ↓ |
| 内存占用 | ~13GB | ~12.5GB | 4% ↓ |
| 并发处理 | 同步 | 异步 | ✓ |
| API文档 | 手动 | 自动 | ✓ |

## 🔧 迁移步骤

### 从v1.3.0升级

1. **停止旧服务**
```bash
docker-compose down
```

2. **更新配置**
```bash
# 下载新的docker-compose.yml
wget https://raw.githubusercontent.com/neosun100/GLM-TTS-Enhanced/main/docker-compose.yml
```

3. **启动新服务**
```bash
docker-compose up -d
```

4. **验证**
```bash
curl http://localhost:8080/health
```

### 客户端代码更新

如果你有自定义客户端调用流式接口：

```javascript
// 旧代码
fetch('http://localhost:8081/api/tts/stream', {...})

// 新代码
fetch('http://localhost:8080/api/tts', {
    ...
    headers: {'Accept': 'text/event-stream'}
})
```

## 🐛 已知问题

1. **HTML模板路径**: 确保 `templates/index.html` 存在
2. **静态文件**: `/voices` 路径映射到 `TEMP_DIR`

## 📝 回滚方案

如遇问题可回滚到v1.3.0：

```bash
docker-compose down
docker pull neosun/glm-tts:v1.3.0
# 使用v1.3.0的docker-compose.yml
docker-compose up -d
```

## 🎯 未来计划

- [ ] WebSocket支持
- [ ] 真正增量流式（集成token2wav_stream）
- [ ] 多语言支持
- [ ] 批量处理API

## 📞 支持

- GitHub Issues: https://github.com/neosun100/GLM-TTS-Enhanced/issues
- 文档: https://github.com/neosun100/GLM-TTS-Enhanced

---

**v2.0.0 - 2025-12-12**
完全迁移到FastAPI，统一接口，更好的性能和开发体验！
