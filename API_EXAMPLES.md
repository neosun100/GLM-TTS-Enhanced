# GLM-TTS API 使用示例

## 基础信息

- **服务地址**: http://0.0.0.0:8080
- **API 文档**: http://0.0.0.0:8080/apidocs/
- **内容类型**: multipart/form-data (TTS), application/json (其他)

---

## 1. 健康检查

### cURL
```bash
curl http://0.0.0.0:8080/health
```

### Python
```python
import requests

response = requests.get('http://0.0.0.0:8080/health')
print(response.json())
# {'status': 'ok', 'model_loaded': False}
```

### JavaScript
```javascript
fetch('http://0.0.0.0:8080/health')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 2. GPU 状态查询

### cURL
```bash
curl http://0.0.0.0:8080/api/gpu/status
```

### Python
```python
import requests

response = requests.get('http://0.0.0.0:8080/api/gpu/status')
status = response.json()
print(f"GPU 已加载: {status['loaded']}")
print(f"显存使用: {status['gpu_memory_used']} MB / {status['gpu_memory_total']} MB")
```

### 响应示例
```json
{
  "gpu_memory_total": 46068,
  "gpu_memory_used": 7460,
  "loaded": false
}
```

---

## 3. GPU 显存释放

### cURL
```bash
curl -X POST http://0.0.0.0:8080/api/gpu/offload
```

### Python
```python
import requests

response = requests.post('http://0.0.0.0:8080/api/gpu/offload')
print(response.json())
# {'status': 'offloaded'}
```

---

## 4. 文本转语音 (核心功能)

### cURL
```bash
curl -X POST http://0.0.0.0:8080/api/tts \
  -F "text=你好，这是一个测试" \
  -F "prompt_audio=@examples/prompt/jiayan_en1.wav" \
  -F "prompt_text=参考文本" \
  -o output.wav
```

### Python
```python
import requests

# 准备数据
files = {
    'prompt_audio': open('examples/prompt/jiayan_en1.wav', 'rb')
}
data = {
    'text': '你好，这是一个测试',
    'prompt_text': '参考文本'
}

# 发送请求
response = requests.post(
    'http://0.0.0.0:8080/api/tts',
    files=files,
    data=data
)

# 保存音频
if response.status_code == 200:
    with open('output.wav', 'wb') as f:
        f.write(response.content)
    print("音频生成成功！")
else:
    print(f"错误: {response.json()}")
```

### JavaScript (Node.js)
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('text', '你好，这是一个测试');
form.append('prompt_audio', fs.createReadStream('examples/prompt/jiayan_en1.wav'));
form.append('prompt_text', '参考文本');

axios.post('http://0.0.0.0:8080/api/tts', form, {
  headers: form.getHeaders(),
  responseType: 'arraybuffer'
})
.then(response => {
  fs.writeFileSync('output.wav', response.data);
  console.log('音频生成成功！');
})
.catch(error => console.error('错误:', error));
```

### JavaScript (浏览器)
```javascript
const formData = new FormData();
formData.append('text', '你好，这是一个测试');
formData.append('prompt_audio', fileInput.files[0]);
formData.append('prompt_text', '参考文本');

fetch('http://0.0.0.0:8080/api/tts', {
  method: 'POST',
  body: formData
})
.then(response => response.blob())
.then(blob => {
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  audio.play();
});
```

---

## 5. 批量处理示例

### Python - 批量生成
```python
import requests
import os

texts = [
    "第一段文本",
    "第二段文本",
    "第三段文本"
]

prompt_audio = 'examples/prompt/jiayan_en1.wav'

for i, text in enumerate(texts):
    files = {'prompt_audio': open(prompt_audio, 'rb')}
    data = {'text': text}
    
    response = requests.post(
        'http://0.0.0.0:8080/api/tts',
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        output_path = f'output_{i+1}.wav'
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ {output_path} 生成成功")
    else:
        print(f"❌ 第 {i+1} 段失败: {response.json()}")
```

---

## 6. 错误处理

### Python 完整示例
```python
import requests

def generate_speech(text, prompt_audio_path, output_path):
    """
    生成语音的完整函数，包含错误处理
    """
    try:
        # 检查服务健康
        health = requests.get('http://0.0.0.0:8080/health', timeout=5)
        if health.json()['status'] != 'ok':
            raise Exception("服务不可用")
        
        # 准备请求
        files = {'prompt_audio': open(prompt_audio_path, 'rb')}
        data = {'text': text}
        
        # 发送请求
        response = requests.post(
            'http://0.0.0.0:8080/api/tts',
            files=files,
            data=data,
            timeout=60
        )
        
        # 检查响应
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return {'success': True, 'output': output_path}
        else:
            error = response.json().get('error', 'Unknown error')
            return {'success': False, 'error': error}
    
    except requests.exceptions.Timeout:
        return {'success': False, 'error': '请求超时'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': '无法连接到服务器'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# 使用示例
result = generate_speech(
    text="测试文本",
    prompt_audio_path="examples/prompt/jiayan_en1.wav",
    output_path="output.wav"
)

if result['success']:
    print(f"✅ 成功: {result['output']}")
else:
    print(f"❌ 失败: {result['error']}")
```

---

## 7. 性能优化建议

### 1. 复用连接
```python
import requests

# 创建 Session 复用连接
session = requests.Session()

for text in texts:
    response = session.post(...)  # 使用 session 而不是 requests
```

### 2. 并发请求
```python
from concurrent.futures import ThreadPoolExecutor
import requests

def generate_one(text):
    # ... TTS 请求代码
    pass

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(generate_one, texts)
```

### 3. 流式处理（大文件）
```python
response = requests.post(..., stream=True)

with open('output.wav', 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
```

---

## 8. 监控和调试

### 监控 GPU 使用
```python
import requests
import time

while True:
    status = requests.get('http://0.0.0.0:8080/api/gpu/status').json()
    print(f"GPU: {status['gpu_memory_used']} MB / {status['gpu_memory_total']} MB")
    time.sleep(5)
```

### 检查服务日志
```bash
# 如果使用 Docker
docker-compose logs -f

# 如果直接运行
tail -f server.log
```

---

## 9. 常见问题

### Q: 如何处理长文本？
A: 将长文本分段处理，然后合并音频文件。

### Q: 支持哪些音频格式？
A: 输入支持常见格式（WAV, MP3 等），输出为 WAV 格式。

### Q: 如何提高音质？
A: 使用高质量的参考音频（清晰、无噪音、3-10秒）。

### Q: API 有速率限制吗？
A: 当前版本无速率限制，但建议控制并发数量。

---

## 10. 完整工作流示例

```python
import requests
import time

class GLMTTSClient:
    def __init__(self, base_url='http://0.0.0.0:8080'):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """健康检查"""
        response = self.session.get(f'{self.base_url}/health')
        return response.json()
    
    def get_gpu_status(self):
        """获取 GPU 状态"""
        response = self.session.get(f'{self.base_url}/api/gpu/status')
        return response.json()
    
    def offload_gpu(self):
        """释放 GPU"""
        response = self.session.post(f'{self.base_url}/api/gpu/offload')
        return response.json()
    
    def text_to_speech(self, text, prompt_audio_path, output_path, prompt_text=''):
        """文本转语音"""
        files = {'prompt_audio': open(prompt_audio_path, 'rb')}
        data = {'text': text, 'prompt_text': prompt_text}
        
        response = self.session.post(
            f'{self.base_url}/api/tts',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return {'success': True, 'output': output_path}
        else:
            return {'success': False, 'error': response.json()}

# 使用示例
client = GLMTTSClient()

# 1. 检查服务
print("检查服务状态...")
print(client.health_check())

# 2. 查看 GPU
print("\nGPU 状态:")
print(client.get_gpu_status())

# 3. 生成语音
print("\n生成语音...")
result = client.text_to_speech(
    text="你好，欢迎使用 GLM-TTS",
    prompt_audio_path="examples/prompt/jiayan_en1.wav",
    output_path="welcome.wav"
)
print(result)

# 4. 释放 GPU
print("\n释放 GPU...")
print(client.offload_gpu())
```

---

**更多信息**: 
- API 文档: http://0.0.0.0:8080/apidocs/
- 项目文档: README.md
- MCP 集成: MCP_GUIDE.md
