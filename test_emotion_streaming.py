#!/usr/bin/env python3
"""
GLM-TTS v1.2.0 情感控制和流式推理测试
"""
import requests
import json
import base64
import time

BASE_URL = "http://localhost:8080"

def test_list_emotions():
    """测试1: 列出所有情感类型"""
    print("\n=== 测试1: 列出情感类型 ===")
    resp = requests.get(f"{BASE_URL}/api/emotions")
    data = resp.json()
    print(f"支持的情感: {list(data['emotions'].keys())}")
    for emotion, info in data['emotions'].items():
        print(f"  - {emotion}: {info['description']} (默认强度: {info['intensity']})")
    return resp.status_code == 200

def test_set_emotion(voice_id):
    """测试2: 为voice设置情感"""
    print(f"\n=== 测试2: 设置情感 (voice_id={voice_id}) ===")
    resp = requests.post(
        f"{BASE_URL}/api/voices/{voice_id}/emotion",
        json={'emotion': 'happy', 'intensity': 0.8}
    )
    data = resp.json()
    print(f"设置结果: {data}")
    return resp.status_code == 200

def test_streaming_tts(voice_id):
    """测试3: 流式TTS生成"""
    print(f"\n=== 测试3: 流式生成 (voice_id={voice_id}) ===")
    
    data = {
        'text': '你好，这是一个流式语音合成测试。我们正在测试情感控制功能。',
        'voice_id': voice_id,
        'emotion': 'excited',
        'emotion_intensity': '0.9'
    }
    
    print(f"开始流式生成...")
    start_time = time.time()
    
    resp = requests.post(
        f"{BASE_URL}/api/tts/stream",
        data=data,
        stream=True
    )
    
    chunk_count = 0
    for line in resp.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                chunk_data = json.loads(line_str[6:])
                metadata = chunk_data['metadata']
                
                if metadata['type'] == 'chunk':
                    chunk_count += 1
                    print(f"  收到块 {metadata['index']+1}/{metadata['total']}: {metadata['text'][:20]}...")
                elif metadata['type'] == 'done':
                    print(f"✓ 生成完成，共{chunk_count}个块，耗时{time.time()-start_time:.2f}秒")
    
    return chunk_count > 0

def test_stream_status():
    """测试4: 查询流式状态"""
    print("\n=== 测试4: 流式状态查询 ===")
    resp = requests.get(f"{BASE_URL}/api/tts/stream/status")
    data = resp.json()
    print(f"当前状态: {'生成中' if data['is_generating'] else '空闲'}")
    return resp.status_code == 200

def main():
    print("=" * 60)
    print("GLM-TTS v1.2.0 情感控制和流式推理测试")
    print("=" * 60)
    
    # 使用已有的voice_id（从v1.1.0测试中获取）
    voice_id = "e2d8cdc3"  # 中文语音
    
    results = []
    
    # 执行测试
    results.append(("列出情感类型", test_list_emotions()))
    results.append(("设置情感", test_set_emotion(voice_id)))
    results.append(("流式TTS生成", test_streaming_tts(voice_id)))
    results.append(("流式状态查询", test_stream_status()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 通过")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
