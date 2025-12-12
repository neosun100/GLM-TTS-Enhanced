# 语音固化技术分析

## 🎯 需求理解

**核心需求**：将参考音频的特征提取结果缓存下来，避免每次生成都重新提取，提升速度。

## 📊 当前工作流程

### 完整流程（每次都执行）

```
用户上传参考音频 (reference.wav)
    ↓
1. 提取文本 Token (Whisper识别 + 分词)
    ↓
2. 提取语音 Token (SpeechTokenizer编码)
    ↓
3. 提取语音特征 (Mel频谱)
    ↓
4. 提取说话人嵌入 (Speaker Embedding)
    ↓
5. LLM生成语音Token序列
    ↓
6. Flow模型生成Mel频谱
    ↓
7. Vocoder合成音频波形
    ↓
输出音频 (output.wav)
```

### 时间消耗分析

| 步骤 | 耗时 | 是否可缓存 |
|------|------|-----------|
| 1. Whisper识别 | ~2-3秒 | ✅ 可缓存 |
| 2. 语音Token提取 | ~0.5秒 | ✅ 可缓存 |
| 3. Mel特征提取 | ~0.3秒 | ✅ 可缓存 |
| 4. 说话人嵌入 | ~0.2秒 | ✅ 可缓存 |
| 5. LLM生成 | ~1-2秒 | ❌ 每次不同 |
| 6. Flow生成 | ~0.5秒 | ❌ 每次不同 |
| 7. Vocoder合成 | ~0.3秒 | ❌ 每次不同 |

**结论**：步骤1-4可以缓存，节省约**3-4秒**！

## 🔍 关键代码分析

### 当前实现（glmtts_inference.py）

```python
# 每次都重新提取
prompt_text_token = frontend._extract_text_token(prompt_text+" ")
prompt_speech_token = frontend._extract_speech_token([item["prompt_speech"]])
speech_feat = frontend._extract_speech_feat(item["prompt_speech"], sample_rate=sample_rate)
embedding = frontend._extract_spk_embedding(item["prompt_speech"])
```

### 可缓存的数据结构

```python
voice_cache = {
    "voice_id": "unique_voice_identifier",  # MD5或UUID
    "audio_path": "path/to/reference.wav",
    "audio_md5": "abc123...",               # 音频文件MD5
    "prompt_text": "参考音频的文本",
    "prompt_text_token": tensor([...]),     # 文本Token
    "prompt_speech_token": tensor([...]),   # 语音Token
    "speech_feat": tensor([...]),           # Mel特征
    "embedding": tensor([...]),             # 说话人嵌入
    "sample_rate": 24000,
    "created_at": "2025-12-12 14:00:00",
    "last_used": "2025-12-12 14:30:00"
}
```

## 💡 实现方案

### 方案一：文件系统缓存（推荐）

**优点**：
- ✅ 简单易实现
- ✅ 持久化存储
- ✅ 容器重启不丢失
- ✅ 可以预置常用音色

**缺点**：
- ⚠️ 需要管理磁盘空间
- ⚠️ 需要清理过期缓存

**存储结构**：
```
/tmp/glm-tts-voices/
├── voice_cache/
│   ├── voice_001/
│   │   ├── metadata.json          # 元数据
│   │   ├── reference.wav          # 原始音频
│   │   ├── text_token.pt          # 文本Token
│   │   ├── speech_token.pt        # 语音Token
│   │   ├── speech_feat.pt         # Mel特征
│   │   └── embedding.pt           # 说话人嵌入
│   ├── voice_002/
│   └── ...
└── outputs/
```

### 方案二：内存缓存 + Redis（高级）

**优点**：
- ✅ 访问速度最快
- ✅ 支持分布式
- ✅ 自动过期管理

**缺点**：
- ❌ 需要额外依赖（Redis）
- ❌ 容器重启丢失（除非持久化）
- ❌ 实现复杂度高

## 🚀 推荐实现步骤

### Phase 1: 基础缓存（1-2天）

1. **创建语音缓存管理器**
```python
class VoiceCacheManager:
    def __init__(self, cache_dir="/tmp/glm-tts-voices/voice_cache"):
        self.cache_dir = cache_dir
        
    def save_voice(self, audio_path, text, features):
        """保存语音特征到缓存"""
        voice_id = self._generate_voice_id(audio_path)
        # 保存所有特征
        
    def load_voice(self, voice_id):
        """从缓存加载语音特征"""
        # 返回所有特征
        
    def list_voices(self):
        """列出所有缓存的语音"""
        
    def delete_voice(self, voice_id):
        """删除指定语音缓存"""
```

2. **修改 tts_engine.py**
```python
def generate(self, text, prompt_audio_path, prompt_text="", voice_id=None):
    # 如果提供voice_id，直接从缓存加载
    if voice_id:
        features = cache_manager.load_voice(voice_id)
        prompt_text_token = features['text_token']
        prompt_speech_token = features['speech_token']
        speech_feat = features['speech_feat']
        embedding = features['embedding']
    else:
        # 正常流程：提取特征
        # 提取完成后，保存到缓存
        voice_id = cache_manager.save_voice(...)
    
    # 继续生成流程...
```

3. **API 增强**
```python
# 新增端点
@app.route('/api/voices', methods=['GET'])
def list_voices():
    """列出所有缓存的语音"""
    
@app.route('/api/voices', methods=['POST'])
def create_voice():
    """创建新的语音缓存"""
    
@app.route('/api/voices/<voice_id>', methods=['DELETE'])
def delete_voice(voice_id):
    """删除语音缓存"""
    
@app.route('/api/tts', methods=['POST'])
def generate_tts():
    # 支持 voice_id 参数
    voice_id = request.form.get('voice_id')
    if voice_id:
        # 使用缓存的语音
    else:
        # 上传新音频
```

### Phase 2: UI 增强（1-2天）

1. **语音库管理界面**
```html
<div class="voice-library">
    <h3>我的语音库</h3>
    <div class="voice-list">
        <div class="voice-item">
            <img src="avatar.png" />
            <span>温柔女声</span>
            <button>使用</button>
            <button>删除</button>
        </div>
    </div>
    <button>+ 添加新语音</button>
</div>
```

2. **快速选择**
```html
<select id="voice-selector">
    <option value="">上传新音频</option>
    <option value="voice_001">温柔女声</option>
    <option value="voice_002">磁性男声</option>
</select>
```

### Phase 3: 预置音色（1天）

1. **预置常用音色**
```python
PRESET_VOICES = {
    "gentle_female": {
        "name": "温柔女声",
        "description": "适合有声小说、睡前故事",
        "audio": "presets/gentle_female.wav",
        "text": "这是一段温柔的女声示例"
    },
    "energetic_male": {
        "name": "活力男声",
        "description": "适合新闻播报、广告配音",
        "audio": "presets/energetic_male.wav",
        "text": "这是一段充满活力的男声示例"
    }
}
```

2. **启动时自动加载**
```python
def init_preset_voices():
    for voice_id, config in PRESET_VOICES.items():
        if not cache_manager.exists(voice_id):
            cache_manager.save_voice(
                audio_path=config['audio'],
                text=config['text'],
                voice_id=voice_id
            )
```

## 📈 性能提升预期

### 当前性能
- 首次生成：~5秒（包含特征提取）
- 后续生成：~5秒（每次都重新提取）

### 优化后性能
- 首次生成：~5秒（提取+缓存）
- 使用缓存：~2秒（跳过提取）
- **提升**：60% 速度提升！

## 🎯 用户体验改进

### 改进前
```
1. 上传参考音频
2. 输入参考文本
3. 输入要合成的文本
4. 等待5秒
5. 下载音频

每次都要重复1-2步
```

### 改进后
```
1. 首次：上传音频 → 自动保存到语音库
2. 后续：选择语音库中的音色
3. 输入要合成的文本
4. 等待2秒
5. 下载音频

节省3秒 + 操作更简单
```

## 🔒 安全考虑

1. **存储限制**
   - 单个用户最多缓存10个语音
   - 单个缓存最大100MB
   - 总缓存空间限制1GB

2. **过期清理**
   - 30天未使用自动删除
   - 提供手动清理接口

3. **隐私保护**
   - 音频文件加密存储（可选）
   - 支持设置私有/公开

## 💬 讨论问题

### Q1: 是否需要支持多用户？
**建议**：先实现单用户版本，后续可扩展

### Q2: 缓存存储在哪里？
**建议**：存储在 `/tmp/glm-tts-voices/voice_cache`，与输出文件同目录

### Q3: 如何标识唯一语音？
**建议**：使用音频文件MD5 + 文本内容MD5组合

### Q4: 是否需要预置音色？
**建议**：Phase 1先不做，Phase 3再添加

## 📝 下一步行动

1. **确认方案**：是否采用方案一（文件系统缓存）？
2. **确认范围**：是否先实现Phase 1？
3. **确认接口**：API设计是否满足需求？
4. **开始开发**：创建 `voice_cache.py` 模块

---

**等待您的反馈和决策！** 🚀
