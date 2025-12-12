#!/usr/bin/env python3
"""
语音缓存功能测试脚本
"""
import requests
import json
import time
import os

BASE_URL = "http://localhost:8080"

def test_cache_stats():
    """测试缓存统计"""
    print("\n=== 测试缓存统计 ===")
    response = requests.get(f"{BASE_URL}/api/cache/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_list_voices():
    """测试列出语音"""
    print("\n=== 测试列出语音 ===")
    response = requests.get(f"{BASE_URL}/api/voices")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total voices: {len(data.get('voices', []))}")
    for voice in data.get('voices', []):
        print(f"  - {voice['voice_id']}: {voice['prompt_text'][:30]}...")
    return response.status_code == 200

def test_create_voice(audio_file):
    """测试创建语音缓存"""
    print("\n=== 测试创建语音缓存 ===")
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        return False
    
    with open(audio_file, 'rb') as f:
        files = {'audio': f}
        data = {'prompt_text': '这是一个测试语音'}
        response = requests.post(f"{BASE_URL}/api/voices", files=files, data=data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Voice ID: {result['voice_id']}")
        print(f"Metadata: {json.dumps(result['metadata'], indent=2, ensure_ascii=False)}")
        return result['voice_id']
    else:
        print(f"Error: {response.text}")
        return None

def test_tts_with_voice_id(voice_id, text="你好，这是使用缓存语音的测试。"):
    """测试使用voice_id生成TTS"""
    print(f"\n=== 测试使用voice_id生成TTS ===")
    print(f"Voice ID: {voice_id}")
    print(f"Text: {text}")
    
    data = {
        'text': text,
        'voice_id': voice_id,
        'sampling_strategy': 'balanced'
    }
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/tts", data=data)
    elapsed = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Time: {elapsed:.2f}s")
    
    if response.status_code == 200:
        output_file = f"test_output_voice_{voice_id}.wav"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Saved to: {output_file}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_tts_traditional(audio_file, text="你好，这是传统模式的测试。"):
    """测试传统模式（上传音频）"""
    print(f"\n=== 测试传统模式（上传音频）===")
    print(f"Audio: {audio_file}")
    print(f"Text: {text}")
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}")
        return False
    
    with open(audio_file, 'rb') as f:
        files = {'prompt_audio': f}
        data = {
            'text': text,
            'prompt_text': '参考音频文本',
            'sampling_strategy': 'balanced'
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/tts", files=files, data=data)
        elapsed = time.time() - start_time
    
    print(f"Status: {response.status_code}")
    print(f"Time: {elapsed:.2f}s")
    
    if response.status_code == 200:
        output_file = "test_output_traditional.wav"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Saved to: {output_file}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_delete_voice(voice_id):
    """测试删除语音"""
    print(f"\n=== 测试删除语音 ===")
    print(f"Voice ID: {voice_id}")
    
    response = requests.delete(f"{BASE_URL}/api/voices/{voice_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def main():
    """主测试流程"""
    print("=" * 60)
    print("GLM-TTS 语音缓存功能测试")
    print("=" * 60)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Error: Service not running")
            return
    except:
        print("Error: Cannot connect to service")
        return
    
    # 测试音频文件（需要提供一个测试音频）
    test_audio = "examples/prompt/jiayan_zh.wav"
    
    # 1. 查看初始缓存状态
    test_cache_stats()
    test_list_voices()
    
    # 2. 创建语音缓存
    voice_id = test_create_voice(test_audio)
    if not voice_id:
        print("\n❌ 创建语音缓存失败")
        return
    
    # 3. 再次查看缓存状态
    test_list_voices()
    test_cache_stats()
    
    # 4. 使用voice_id生成TTS（快速模式）
    success = test_tts_with_voice_id(voice_id, "使用缓存语音生成的第一段测试文本。")
    if not success:
        print("\n❌ 使用voice_id生成失败")
        return
    
    # 5. 再次使用同一voice_id（应该更快）
    success = test_tts_with_voice_id(voice_id, "使用缓存语音生成的第二段测试文本，应该更快。")
    if not success:
        print("\n❌ 第二次使用voice_id生成失败")
        return
    
    # 6. 测试传统模式（对比速度）
    success = test_tts_traditional(test_audio, "传统模式生成的测试文本，用于对比速度。")
    if not success:
        print("\n❌ 传统模式生成失败")
        return
    
    # 7. 测试删除语音（可选）
    # test_delete_voice(voice_id)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    print("\n对比结果：")
    print("- 使用voice_id模式：跳过Whisper识别，速度更快")
    print("- 传统模式：每次都需要Whisper识别，速度较慢")
    print("\n生成的测试文件：")
    print(f"- test_output_voice_{voice_id}.wav (使用缓存)")
    print("- test_output_traditional.wav (传统模式)")

if __name__ == "__main__":
    main()
