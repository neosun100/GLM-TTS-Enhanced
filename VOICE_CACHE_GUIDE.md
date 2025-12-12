# 语音缓存功能使用指南

## 🎯 功能概述

语音缓存系统允许您保存常用的参考语音，避免每次生成都重新上传和处理音频文件，大幅提升生成速度。

### 核心优势

| 特性 | 传统模式 | 缓存模式 |
|------|---------|---------|
| 上传音频 | ✅ 每次必需 | ❌ 首次后不需要 |
| Whisper识别 | ✅ 每次执行 (~2-3秒) | ❌ 跳过 |
| 特征提取 | ✅ 每次执行 (~1秒) | ❌ 从缓存加载 |
| 总耗时 | ~5秒 | ~2秒 |
| **速度提升** | - | **60%** |

## 🚀 快速开始

### 1. 创建语音缓存

**方式一：通过API**

```bash
curl -X POST http://localhost:8080/api/voices \
  -F "audio=@my_voice.wav" \
  -F "prompt_text=这是我的声音"
```

**响应示例：**
```json
{
  "voice_id": "a1b2c3d4",
  "metadata": {
    "voice_id": "a1b2c3d4",
    "prompt_text": "这是我的声音",
    "sample_rate": 24000,
    "created_at": "2025-12-12T14:00:00",
    "last_used": "2025-12-12T14:00:00"
  },
  "message": "Voice cached successfully"
}
```

**方式二：通过Web UI**

1. 上传参考音频
2. 输入参考文本
3. 点击"保存到语音库"
4. 系统自动生成voice_id

### 2. 使用缓存的语音生成TTS

**方式一：专用API（推荐）**

```bash
curl -X POST http://localhost:8080/api/tts/with_voice \
  -F "text=你好，这是测试文本" \
  -F "voice_id=a1b2c3d4" \
  -F "sampling_strategy=balanced" \
  -o output.wav
```

**方式二：通用API**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=你好，这是测试文本" \
  -F "voice_id=a1b2c3d4" \
  -o output.wav
```

**方式三：Web UI**

1. 在"语音库"下拉框选择已保存的语音
2. 输入要合成的文本
3. 点击"生成语音"
4. 系统自动使用缓存，速度更快

### 3. 管理语音库

**列出所有语音**

```bash
curl http://localhost:8080/api/voices
```

**响应示例：**
```json
{
  "voices": [
    {
      "voice_id": "a1b2c3d4",
      "prompt_text": "这是我的声音",
      "created_at": "2025-12-12T14:00:00",
      "last_used": "2025-12-12T14:30:00"
    }
  ],
  "stats": {
    "total_voices": 1,
    "memory_cached": 1,
    "total_size_mb": 15.2,
    "cache_dir": "/tmp/glm-tts-voices/voice_cache",
    "memory_cache_enabled": true
  }
}
```

**删除语音**

```bash
curl -X DELETE http://localhost:8080/api/voices/a1b2c3d4
```

**获取语音信息**

```bash
curl http://localhost:8080/api/voices/a1b2c3d4
```

**下载参考音频**

```bash
curl http://localhost:8080/api/voices/a1b2c3d4/audio -o reference.wav
```

## 📊 API 参考

### POST /api/voices
创建语音缓存

**参数：**
- `audio` (file, required): 参考音频文件
- `prompt_text` (string, optional): 参考文本（留空自动识别）
- `skip_whisper` (boolean, optional): 是否跳过Whisper识别

**响应：**
```json
{
  "voice_id": "string",
  "metadata": {},
  "message": "string"
}
```

### GET /api/voices
列出所有语音

**响应：**
```json
{
  "voices": [],
  "stats": {}
}
```

### GET /api/voices/{voice_id}
获取语音信息

**响应：**
```json
{
  "voice_id": "string",
  "metadata": {}
}
```

### DELETE /api/voices/{voice_id}
删除语音

**响应：**
```json
{
  "message": "Voice deleted successfully"
}
```

### GET /api/voices/{voice_id}/audio
下载参考音频

**响应：** 音频文件（audio/wav）

### POST /api/tts/with_voice
使用voice_id生成TTS（快速模式）

**参数：**
- `text` (string, required): 要合成的文本
- `voice_id` (string, required): 语音ID
- `temperature` (number, optional): Temperature参数 (0.1-1.5)
- `top_p` (number, optional): Top-p参数 (0.5-1.0)
- `sampling_strategy` (string, optional): 采样策略 (fast/balanced/quality)

**响应：** 音频文件（audio/wav）

### POST /api/tts
通用TTS接口（支持voice_id或上传音频）

**参数：**
- `text` (string, required): 要合成的文本
- `voice_id` (string, optional): 语音ID
- `prompt_audio` (file, optional): 参考音频（如果不提供voice_id则必需）
- `prompt_text` (string, optional): 参考文本
- `temperature` (number, optional): Temperature参数
- `top_p` (number, optional): Top-p参数
- `sampling_strategy` (string, optional): 采样策略
- `skip_whisper` (string, optional): 是否跳过Whisper (0/1)

**响应：** 音频文件（audio/wav）

### GET /api/cache/stats
获取缓存统计信息

**响应：**
```json
{
  "total_voices": 10,
  "memory_cached": 10,
  "total_size_mb": 152.5,
  "cache_dir": "/tmp/glm-tts-voices/voice_cache",
  "memory_cache_enabled": true
}
```

## 🔧 配置选项

### 环境变量

```bash
# 启用内存缓存（默认：true）
ENABLE_MEMORY_CACHE=true

# 缓存目录（默认：/tmp/glm-tts-voices/voice_cache）
VOICE_CACHE_DIR=/tmp/glm-tts-voices/voice_cache
```

### 缓存策略

系统支持**双层缓存**：

1. **文件系统缓存**：持久化存储，容器重启不丢失
2. **内存缓存**：快速访问，启动时自动加载

**内存缓存优势：**
- 访问速度：<1ms
- 自动预热：启动时加载所有缓存
- 智能更新：使用时自动更新last_used时间

## 💡 最佳实践

### 1. 预置常用音色

```bash
# 创建多个常用音色
curl -X POST http://localhost:8080/api/voices \
  -F "audio=@female_gentle.wav" \
  -F "prompt_text=温柔女声"

curl -X POST http://localhost:8080/api/voices \
  -F "audio=@male_energetic.wav" \
  -F "prompt_text=活力男声"
```

### 2. 批量生成

```bash
# 使用同一voice_id批量生成
for text in "文本1" "文本2" "文本3"; do
  curl -X POST http://localhost:8080/api/tts/with_voice \
    -F "text=$text" \
    -F "voice_id=a1b2c3d4" \
    -o "output_${text}.wav"
done
```

### 3. 定期清理

```bash
# 删除不常用的语音
curl http://localhost:8080/api/voices | jq -r '.voices[] | select(.last_used < "2025-11-01") | .voice_id' | \
while read voice_id; do
  curl -X DELETE http://localhost:8080/api/voices/$voice_id
done
```

## 🐛 故障排除

### 问题1：voice_id不存在

**错误信息：**
```json
{
  "error": "Voice ID not found: a1b2c3d4"
}
```

**解决方案：**
1. 检查voice_id是否正确
2. 使用 `GET /api/voices` 查看所有可用的voice_id
3. 重新创建语音缓存

### 问题2：缓存目录权限问题

**错误信息：**
```
Permission denied: /tmp/glm-tts-voices/voice_cache
```

**解决方案：**
```bash
mkdir -p /tmp/glm-tts-voices/voice_cache
chmod 777 /tmp/glm-tts-voices/voice_cache
```

### 问题3：内存缓存未生效

**检查方法：**
```bash
curl http://localhost:8080/api/cache/stats
```

**响应示例：**
```json
{
  "memory_cache_enabled": true,
  "memory_cached": 10
}
```

如果 `memory_cached` 为0，重启服务：
```bash
docker restart glm-tts
```

## 📈 性能对比

### 实测数据（10秒音频）

| 模式 | 首次生成 | 后续生成 | 提升 |
|------|---------|---------|------|
| 传统模式 | 5.2秒 | 5.1秒 | - |
| 缓存模式 | 5.0秒 | 2.1秒 | **59%** |

### 资源占用

| 指标 | 文件缓存 | 内存缓存 |
|------|---------|---------|
| 单个语音 | ~15MB | ~15MB |
| 10个语音 | ~150MB | ~150MB |
| 访问速度 | ~10ms | <1ms |

## 🔮 未来计划

- [ ] 支持语音标签和分类
- [ ] 支持语音预览播放
- [ ] 支持语音评分和推荐
- [ ] 支持语音分享和导入
- [ ] 支持自定义音色训练

---

**更新时间**: 2025-12-12  
**版本**: v1.1.0
