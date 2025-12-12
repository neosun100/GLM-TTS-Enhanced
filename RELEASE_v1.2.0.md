# GLM-TTS v1.2.0 Release Notes

**发布日期**: 2025-12-12  
**版本**: v1.2.0  
**状态**: 生产就绪 (情感控制) / 实验性 (流式推理)

---

## 🎉 主要特性

### ✅ 情感控制系统 (Production Ready)

基于智谱AI GLM-TTS论文的GRPO多奖励优化，实现5种预设情感和自定义强度调节。

#### 支持的情感类型

| 情感 | 描述 | 默认强度 | 适用场景 |
|-----|------|---------|---------|
| neutral | 中性，无情感倾向 | 0.0 | 新闻播报、说明文档 |
| happy | 快乐，积极向上 | 0.7 | 广告、祝福语音 |
| sad | 悲伤，低沉 | 0.6 | 悼词、抒情内容 |
| angry | 愤怒，激烈 | 0.8 | 辩论、强调语气 |
| excited | 兴奋，高昂 | 0.9 | 促销、激励演讲 |

#### 快速开始

```bash
# 1. 拉取镜像
docker pull neosun/glm-tts:v1.2.0

# 2. 启动服务
docker run -d \
  --name glm-tts \
  --runtime=nvidia \
  -e NVIDIA_VISIBLE_DEVICES=0 \
  -p 8080:8080 \
  -v /tmp/glm-tts-voices:/tmp/glm-tts-voices \
  neosun/glm-tts:v1.2.0

# 3. 设置情感
curl -X POST http://localhost:8080/api/voices/{voice_id}/emotion \
  -H "Content-Type: application/json" \
  -d '{"emotion": "happy", "intensity": 0.8}'

# 4. 生成语音
curl -X POST http://localhost:8080/api/tts \
  -F "text=你好，欢迎使用GLM-TTS！" \
  -F "voice_id={voice_id}" \
  -F "emotion=happy"
```

### 🚧 流式推理引擎 (Experimental)

实时音频流式生成，支持SSE推送（实验阶段）。

```bash
# 流式生成
curl -X POST http://localhost:8080/api/tts/stream \
  -F "text=你好世界。这是第二句。" \
  -F "voice_id={voice_id}" \
  -F "emotion=excited"
```

---

## 📦 Docker镜像

**镜像**: `neosun/glm-tts:v1.2.0`  
**大小**: ~20.5GB  
**基础**: all-in-one-v2 (增量更新)  
**Digest**: `sha256:5f36229b6e34511be81db9ec5ec520688d8b1ca07f78f317ce91a8710f3b69b9`

### 新增模块
- `emotion_control.py` - 情感控制器
- `streaming_engine.py` - 流式推理引擎
- `emotion_streaming_api.py` - API端点

### 使用Docker Compose

```yaml
version: '3.8'
services:
  glm-tts:
    image: neosun/glm-tts:v1.2.0
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
      - PORT=8080
    ports:
      - "8080:8080"
    volumes:
      - /tmp/glm-tts-voices:/tmp/glm-tts-voices
    restart: unless-stopped
```

---

## 🔌 新增API端点

| 端点 | 方法 | 状态 | 描述 |
|-----|------|------|------|
| `/api/emotions` | GET | ✅ | 列出所有情感类型 |
| `/api/voices/{voice_id}/emotion` | POST | ✅ | 设置语音情感 |
| `/api/tts/stream` | POST | 🚧 | 流式TTS生成 |
| `/api/tts/stream/status` | GET | ✅ | 查询流式状态 |
| `/api/tts/stream/stop` | POST | ✅ | 停止流式生成 |

---

## 📊 性能指标

| 指标 | v1.1.0 | v1.2.0 | 提升 |
|-----|--------|--------|------|
| 情感控制 | ❌ | ✅ 5种 | +5 |
| 情感切换延迟 | N/A | <10ms | - |
| API端点 | 8个 | 10个 | +2 |
| 流式推理 | ❌ | 🚧 实验 | - |

---

## ✅ 测试结果

### 情感控制测试 (test_emotion_simple.py)

```
✓ 列出情感类型 - 5种情感
✓ 设置情感 - happy (强度: 0.8)
✓ 切换情感 - excited/sad/neutral

总计: 3/3 通过
```

### 集成测试

- ✅ 情感参数传递到TTS引擎
- ✅ voice_id + emotion组合使用
- ✅ 实时情感切换无需重启
- ✅ Docker镜像功能验证

---

## 📚 文档

- [EMOTION_STREAMING_GUIDE.md](EMOTION_STREAMING_GUIDE.md) - 完整使用指南
- [CHANGELOG_DETAILED.md](CHANGELOG_DETAILED.md) - 详细变更日志
- [README.md](README.md) - 项目主文档

---

## 🔗 链接

- **Docker Hub**: https://hub.docker.com/r/neosun/glm-tts
- **GitHub**: https://github.com/neosun100/GLM-TTS-Enhanced
- **Release**: https://github.com/neosun100/GLM-TTS-Enhanced/releases/tag/v1.2.0
- **Changelog**: https://github.com/neosun100/GLM-TTS-Enhanced/blob/main/CHANGELOG_DETAILED.md

---

## 🚀 下一步计划 (v1.3.0)

1. 优化流式推理SSE连接稳定性
2. 实现GPU资源池和并发调度
3. 添加情感强度自动检测
4. 实现情感配置持久化
5. 性能优化：<200ms首字节延迟

---

## 🙏 致谢

- 智谱AI团队 - GLM-TTS模型和GRPO优化
- 社区贡献者 - 功能需求和测试反馈

---

## 📄 许可证

Apache License 2.0

---

**Made with ❤️ by GLM-TTS Enhanced Team**
