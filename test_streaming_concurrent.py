#!/usr/bin/env python3
"""GLM-TTS v1.2.0 流式推理和并发测试"""
import requests
import json
import time
import threading

BASE_URL = "http://localhost:8080"

def test_streaming():
    """测试流式生成"""
    print("\n=== 测试: 流式TTS生成 ===")
    
    data = {
        'text': '你好世界。这是第二句话。这是第三句话。',
        'voice_id': 'e2d8cdc3',
        'emotion': 'happy',
        'emotion_intensity': '0.8'
    }
    
    start = time.time()
    resp = requests.post(f"{BASE_URL}/api/tts/stream", data=data, stream=True)
    
    chunks = 0
    for line in resp.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8')[6:])
                if data['metadata']['type'] == 'chunk':
                    chunks += 1
                    print(f"  收到块 {chunks}: {data['metadata']['text']}")
                elif data['metadata']['type'] == 'done':
                    print(f"✓ 完成，共{chunks}块，耗时{time.time()-start:.2f}秒")
            except:
                pass
    
    return chunks > 0

def concurrent_request(thread_id, results):
    """并发请求"""
    try:
        start = time.time()
        resp = requests.post(
            f"{BASE_URL}/api/tts",
            files={'prompt_audio': open('/tmp/glm-tts-voices/voice_cache/e2d8cdc3/reference.wav', 'rb')},
            data={
                'text': f'线程{thread_id}测试',
                'voice_id': 'e2d8cdc3',
                'emotion': 'neutral'
            }
        )
        elapsed = time.time() - start
        results[thread_id] = {'success': resp.status_code == 200, 'time': elapsed}
        print(f"  线程{thread_id}: {elapsed:.2f}秒")
    except Exception as e:
        results[thread_id] = {'success': False, 'error': str(e)}

def test_concurrent():
    """测试并发"""
    print("\n=== 测试: 并发请求 (4路) ===")
    
    threads = []
    results = {}
    
    start = time.time()
    for i in range(4):
        t = threading.Thread(target=concurrent_request, args=(i, results))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    total_time = time.time() - start
    success = sum(1 for r in results.values() if r.get('success'))
    
    print(f"✓ 完成: {success}/4成功，总耗时{total_time:.2f}秒")
    return success >= 3

print("=" * 60)
print("GLM-TTS v1.2.0 流式推理和并发测试")
print("=" * 60)

results = []
results.append(("流式生成", test_streaming()))
results.append(("并发请求", test_concurrent()))

print("\n" + "=" * 60)
for name, passed in results:
    print(f"{'✓' if passed else '✗'} {name}")
print("=" * 60)
