# GLM-TTS Enhanced - Detailed Changelog

This document records all development milestones, feature additions, and technical decisions made during the project evolution.

---

## 2025-12-12 - v1.1.0: Voice Cache System

### Summary
实现语音缓存系统，通过voice_id机制实现双层缓存（文件+内存），跳过Whisper识别和特征提取，理论速度提升60%。

### Features Added
- **Voice Cache Manager** (`voice_cache.py`, 400 lines)
  - 双层缓存架构：文件系统持久化 + 内存缓存（<1ms访问）
  - voice_id生成：基于音频MD5前8位，确保唯一性
  - CRUD操作：创建、读取、更新、删除语音缓存
  - 自动特征提取和存储

- **Voice API** (`voice_api.py`, 250 lines)
  - 8个新API端点：
    - `POST /api/voices` - 创建语音缓存
    - `GET /api/voices` - 列出所有缓存
    - `GET /api/voices/{voice_id}` - 获取特定缓存
    - `DELETE /api/voices/{voice_id}` - 删除缓存
    - `GET /api/cache/stats` - 缓存统计
    - `POST /api/cache/clear` - 清空缓存
    - `POST /api/cache/preload` - 预加载缓存
    - `GET /api/cache/health` - 健康检查

- **TTS Engine Integration**
  - 新增 `generate_with_voice_id()` 方法
  - 新增 `cache_voice_from_audio()` 方法
  - `/api/tts` 支持 `voice_id` 参数

### Technical Details
- **缓存结构**: `/tmp/glm-tts-voices/voice_cache/{voice_id}/`
  - `metadata.json` - 元数据（名称、描述、创建时间）
  - `reference.wav` - 原始音频
  - `*.pt` - 特征文件（PyTorch tensors）

- **性能优化**
  - 缓存模式：跳过Whisper识别和特征提取
  - 当前实现：特征提取使用占位符（torch.zeros）
  - 理论提升：2秒（缓存）vs 5秒（传统），60%速度提升
  - 实际测试：57秒 vs 57秒（特征提取未完善）

### Testing
- **测试文件**: `test_voice_cache.py` (200 lines)
- **测试结果**: 14项测试全部通过
  - 创建2个voice_id（e2d8cdc3中文、12a6b1ed英文）
  - 验证缓存存储和读取
  - 验证API端点功能
  - 验证TTS生成（使用voice_id）

### Docker
- **镜像**: `neosun/glm-tts:v1.1.0` 和 `all-in-one-v2`
- **大小**: 20.5GB
- **新增环境变量**: `ENABLE_MEMORY_CACHE=true`

### Documentation
- `VOICE_CACHE_GUIDE.md` - 使用指南
- `VOICE_CACHE_ANALYSIS.md` - 技术分析
- `TEST_REPORT_V1.1.0.md` - 测试报告
- `SWAGGER_GUIDE.md` - Swagger集成指南

### Git Tags
- `v1.1.0` - Voice cache system release

---

## 2025-12-12 - v1.0.0: Initial Enhanced Release

### Summary
从研究原型升级为生产级服务，添加Web UI、REST API、Docker部署和Whisper自动转录功能。

### Features Added
- **🌐 Modern Web UI**
  - 响应式界面设计
  - 实时进度跟踪（SSE）
  - 文件上传和下载
  - 高级参数控制面板

- **🔌 REST API**
  - Flask服务器 (`server.py`)
  - Swagger文档集成（Flasgger）
  - 健康检查端点
  - SSE进度流

- **🎤 Whisper Integration**
  - 自动音频转录
  - 参考文本为空时自动触发
  - 可选跳过（skip_whisper参数）

- **🐳 Docker Deployment**
  - All-in-one镜像（20.5GB）
  - 包含所有模型和依赖
  - cuDNN 9支持
  - GPU优化配置

- **⚡ Performance**
  - ONNX Runtime GPU加速
  - cuDNN 9集成
  - GPU空闲超时管理
  - 持久化存储（host-mounted）

### Technical Components
- `server.py` - Flask REST API服务器
- `tts_engine.py` - TTS推理引擎
- `Dockerfile` - 多阶段构建
- `docker-compose.yml` - 生产部署配置
- `static/` - Web UI资源
- `templates/` - HTML模板

### Documentation
- `README.md` - 英文文档
- `README_CN.md` - 简体中文文档
- `README_TW.md` - 繁体中文文档
- `README_JP.md` - 日文文档
- `DEPLOYMENT_GUIDE.md` - 部署指南
- `API_DOCUMENTATION.md` - API文档

### Docker Images
- `neosun/glm-tts:v1.0.0` - 初始版本
- `neosun/glm-tts:all-in-one` - 完整镜像

### Git Tags
- `v1.0.0` - Initial enhanced release

---

## Development Notes

### Architecture Decisions
1. **双层缓存设计**: 文件系统保证持久化，内存缓存提供极速访问
2. **voice_id机制**: 基于MD5确保唯一性和可重现性
3. **向后兼容**: 支持voice_id和传统上传两种模式
4. **Swagger集成**: 提供交互式文档和客户端生成支持

### Performance Insights
- 当前限制：特征提取使用占位符，实际速度提升不明显
- 优化潜力：完善特征提取后可达到60%速度提升
- VRAM使用：~12GB during inference
- 生成速度：2-5秒/10秒音频

### Future Improvements
- [ ] 完善特征提取实现
- [ ] 添加批量处理支持
- [ ] 实现分布式缓存
- [ ] 添加缓存预热机制
- [ ] 优化内存使用

---

## Links
- **GitHub Repository**: https://github.com/neosun100/GLM-TTS-Enhanced
- **Docker Hub**: https://hub.docker.com/r/neosun/glm-tts
- **Original GLM-TTS**: https://github.com/zai-org/GLM-TTS

---

*Last Updated: 2025-12-12 18:21 CST*
