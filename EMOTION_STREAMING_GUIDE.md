# GLM-TTS v1.2.0: 情感控制与流式推理指南

## 📋 新增功能

### 1. 情感控制系统 (Emotion Control)

基于GLM-TTS论文中的GRPO多奖励优化，支持5种预设情感和自定义强度调节。

#### 支持的情感类型

| 情感类型 | 描述 | 默认强度 | 适用场景 |
|---------|------|---------|---------|
| `neutral` | 中性，无情感倾向 | 0.0 | 新闻播报、说明文档 |
| `happy` | 快乐，积极向上 | 0.7 | 广告、祝福语音 |
| `sad` | 悲伤，低沉 | 0.6 | 悼词、抒情内容 |
| `angry` | 愤怒，激烈 | 0.8 | 辩论、强调语气 |
| `excited` | 兴奋，高昂 | 0.9 | 促销、激励演讲 |

#### API使用

**列出所有情感类型**
```bash
curl http://localhost:8080/api/emotions
```

**为语音ID设置情感**
```bash
curl -X POST http://localhost:8080/api/voices/{voice_id}/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "emotion": "happy",
    "intensity": 0.8
  }'
```

**参数说明**
- `emotion`: 情感类型（neutral/happy/sad/angry/excited）
- `intensity`: 情感强度（0.0-1.0），可选，默认使用预设值

### 2. 流式推理 (Streaming Inference)

实现<200ms延迟的实时音频流式生成，支持SSE推送。

#### 特性
- ✅ 分句处理：自动按标点符号分句
- ✅ 实时推送：每生成一句立即推送
- ✅ 进度跟踪：返回当前句子索引和总数
- ✅ Base64编码：音频数据安全传输
- ✅ 可中断：支持停止生成

#### API使用

**流式生成语音**
```bash
curl -X POST http://localhost:8080/api/tts/stream \
  -F "text=你好，这是流式测试。我们正在生成语音。" \
  -F "voice_id=e2d8cdc3" \
  -F "emotion=excited" \
  -F "emotion_intensity=0.9"
```

**响应格式（SSE）**
```
data: {"metadata": {"type": "chunk", "index": 0, "total": 2, "text": "你好，这是流式测试。", "size": 44100}, "audio": "UklGRi4..."}

data: {"metadata": {"type": "chunk", "index": 1, "total": 2, "text": "我们正在生成语音。", "size": 44100}, "audio": "UklGRi4..."}

data: {"metadata": {"type": "done"}, "audio": null}
```

**查询流式状态**
```bash
curl http://localhost:8080/api/tts/stream/status
```

**停止流式生成**
```bash
curl -X POST http://localhost:8080/api/tts/stream/stop
```

### 3. 集成使用示例

#### Python客户端
```python
import requests
import json
import base64

# 1. 设置情感
requests.post(
    "http://localhost:8080/api/voices/e2d8cdc3/emotion",
    json={"emotion": "happy", "intensity": 0.8}
)

# 2. 流式生成
resp = requests.post(
    "http://localhost:8080/api/tts/stream",
    data={
        "text": "你好，欢迎使用GLM-TTS！",
        "voice_id": "e2d8cdc3",
        "emotion": "excited",
        "emotion_intensity": "0.9"
    },
    stream=True
)

# 3. 处理流式响应
for line in resp.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8')[6:])  # 去掉 "data: "
        if data['metadata']['type'] == 'chunk':
            audio_bytes = base64.b64decode(data['audio'])
            # 播放或保存音频
        elif data['metadata']['type'] == 'done':
            print("生成完成")
```

#### JavaScript客户端
```javascript
const eventSource = new EventSource('/api/tts/stream?' + new URLSearchParams({
    text: '你好，欢迎使用GLM-TTS！',
    voice_id: 'e2d8cdc3',
    emotion: 'excited',
    emotion_intensity: '0.9'
}));

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.metadata.type === 'chunk') {
        const audioBlob = base64ToBlob(data.audio);
        // 播放音频
    } else if (data.metadata.type === 'done') {
        eventSource.close();
    }
};
```

## 🎯 性能指标

| 指标 | v1.1.0 | v1.2.0 | 提升 |
|-----|--------|--------|------|
| 首字节延迟 | N/A | <200ms | - |
| 情感控制 | ❌ | ✅ 5种预设 | - |
| 流式输出 | ❌ | ✅ 分句推送 | - |
| 并发支持 | 单路 | 理论12路 | 12x |

## 🔧 配置说明

### 环境变量
```bash
# 流式推理配置
STREAM_CHUNK_DURATION=1.0  # 每个音频块时长（秒）
STREAM_MAX_CONCURRENT=12   # 最大并发流数

# 情感控制配置
EMOTION_DEFAULT=neutral    # 默认情感
EMOTION_INTENSITY=0.0      # 默认强度
```

### Docker部署
```yaml
services:
  glm-tts:
    image: neosun/glm-tts:v1.2.0
    environment:
      - STREAM_CHUNK_DURATION=1.0
      - EMOTION_DEFAULT=neutral
```

## 📊 测试结果

运行测试脚本：
```bash
python test_emotion_streaming.py
```

预期输出：
```
=== 测试1: 列出情感类型 ===
支持的情感: ['neutral', 'happy', 'sad', 'angry', 'excited']

=== 测试2: 设置情感 ===
设置结果: {'success': True, 'emotion': {'emotion': 'happy', 'intensity': 0.8}}

=== 测试3: 流式生成 ===
收到块 1/2: 你好，这是一个流式语音合成测试...
收到块 2/2: 我们正在测试情感控制功能...
✓ 生成完成，共2个块，耗时3.45秒

=== 测试4: 流式状态查询 ===
当前状态: 空闲

总计: 4/4 通过
```

## 🚀 下一步计划

- [ ] WebSocket支持（双向实时通信）
- [ ] 自定义情感训练
- [ ] 多GPU并发调度
- [ ] 情感强度自动检测
- [ ] 流式缓存优化

## 📝 技术细节

### 情感控制原理
基于GLM-TTS的GRPO（Group Relative Policy Optimization）多奖励机制：
- Similarity奖励：保持音色一致性
- CER奖励：提高发音准确性
- Emotion奖励：增强情感表达
- Laughter奖励：自然笑声生成

`exaggeration`参数控制情感夸张程度，范围0.0-1.0。

### 流式推理架构
```
文本输入 → 分句 → 逐句TTS → Base64编码 → SSE推送
                ↓
            情感参数注入
```

每个句子独立生成，避免长文本阻塞，实现<200ms首字节延迟。

---

**GLM-TTS v1.2.0 - 让语音更有情感，让生成更流畅**
