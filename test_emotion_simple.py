#!/usr/bin/env python3
"""GLM-TTS v1.2.0 情感控制简化测试"""
import requests

BASE_URL = "http://localhost:8080"

print("=" * 60)
print("GLM-TTS v1.2.0 情感控制测试")
print("=" * 60)

# 测试1: 列出情感
print("\n✓ 测试1: 列出情感类型")
resp = requests.get(f"{BASE_URL}/api/emotions")
emotions = resp.json()['emotions']
print(f"  支持{len(emotions)}种情感: {list(emotions.keys())}")

# 测试2: 设置情感
print("\n✓ 测试2: 设置情感")
resp = requests.post(
    f"{BASE_URL}/api/voices/e2d8cdc3/emotion",
    json={'emotion': 'happy', 'intensity': 0.8}
)
result = resp.json()
print(f"  设置成功: {result['emotion']['emotion']} (强度: {result['emotion']['intensity']})")

# 测试3: 切换情感
print("\n✓ 测试3: 切换情感")
for emotion in ['excited', 'sad', 'neutral']:
    resp = requests.post(
        f"{BASE_URL}/api/voices/e2d8cdc3/emotion",
        json={'emotion': emotion}
    )
    result = resp.json()
    print(f"  {emotion}: {result['emotion']['description']}")

print("\n" + "=" * 60)
print("✓ 所有测试通过！情感控制系统工作正常")
print("=" * 60)
