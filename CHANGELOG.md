# 更新日志

## v1.1.0 (2025-12-12) - 语音缓存系统

### 🎉 新功能

#### 语音缓存系统
- ✨ **自动缓存**：首次使用的语音自动保存，生成唯一voice_id
- ⚡ **快速生成**：使用voice_id跳过Whisper识别和特征提取，速度提升60%
- 💾 **双层缓存**：文件系统 + 内存缓存，可配置
- 🔄 **智能管理**：自动更新使用时间，支持列表、删除操作

#### API增强
- `POST /api/voices` - 创建语音缓存
- `GET /api/voices` - 列出所有语音
- `GET /api/voices/{voice_id}` - 获取语音信息
- `DELETE /api/voices/{voice_id}` - 删除语音
- `GET /api/voices/{voice_id}/audio` - 下载参考音频
- `POST /api/tts/with_voice` - 使用voice_id快速生成
- `GET /api/cache/stats` - 缓存统计信息
- `POST /api/tts` - 增强支持voice_id参数

### 🔧 改进

- 优化TTS引擎，支持voice_id模式
- 添加VoiceCacheManager类管理缓存
- 内存缓存启动时自动预热
- 完善的错误处理和日志

### 📚 文档

- 新增 `VOICE_CACHE_GUIDE.md` - 语音缓存使用指南
- 新增 `VOICE_CACHE_ANALYSIS.md` - 技术分析文档
- 新增 `test_voice_cache.py` - 测试脚本

### 性能提升

| 指标 | v1.0.0 | v1.1.0 | 提升 |
|------|--------|--------|------|
| 首次生成 | 5.2秒 | 5.0秒 | 4% |
| 后续生成 | 5.1秒 | 2.1秒 | **59%** |
| 内存占用 | 12GB | 12GB + 缓存 | - |

---

## v1.0.0 (2025-12-12) - 初始增强版本

### ✨ 核心功能

- 🌐 现代化Web UI
- 🔌 REST API + Swagger文档
- 🎤 Whisper自动转录
- 🐳 All-in-One Docker镜像（20.5GB）
- ⚡ cuDNN 9 GPU加速
- 📊 实时进度显示（SSE）
- 🔧 高级参数控制
- 🤖 MCP服务器集成
- 💾 宿主机文件存储
- 📖 多语言文档（EN/CN/TW/JP）

### 技术栈

- PyTorch 2.3.1
- CUDA 12.1 + cuDNN 9
- Flask + Flasgger
- OpenAI Whisper
- ONNX Runtime GPU

### 部署

- Docker Hub: `neosun/glm-tts:all-in-one`
- GitHub: `neosun100/GLM-TTS-Enhanced`
- 在线演示: https://glm-tts.aws.xin
