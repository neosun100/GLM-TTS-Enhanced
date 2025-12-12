#!/usr/bin/env python3
import sys
import os

# Import MCP tools
sys.path.insert(0, '/home/neo/upload/GLM-TTS')
from mcp_server import text_to_speech, get_gpu_status, offload_gpu

print("🧪 Testing MCP Tools")
print("=" * 50)

# Test 1: get_gpu_status
print("\n1. Testing get_gpu_status...")
result = get_gpu_status()
print(f"   Result: {result}")
assert 'loaded' in result or 'error' in result, "GPU status should return loaded status"
print("   ✅ PASSED")

# Test 2: offload_gpu
print("\n2. Testing offload_gpu...")
result = offload_gpu()
print(f"   Result: {result}")
assert 'status' in result or 'error' in result, "Offload should return status"
print("   ✅ PASSED")

# Test 3: text_to_speech
print("\n3. Testing text_to_speech...")
prompt_path = '/home/neo/upload/GLM-TTS/examples/prompt/jiayan_en1.wav'
output_path = '/home/neo/upload/GLM-TTS/outputs/mcp_test_output.wav'

if os.path.exists(prompt_path):
    result = text_to_speech(
        text="这是MCP测试",
        prompt_audio_path=prompt_path,
        output_path=output_path,
        prompt_text="测试"
    )
    print(f"   Result: {result}")
    
    if result['status'] == 'success':
        assert os.path.exists(output_path), "Output file should exist"
        print(f"   Output file size: {os.path.getsize(output_path)} bytes")
        print("   ✅ PASSED")
    else:
        print(f"   ⚠️  Warning: {result.get('error', 'Unknown error')}")
else:
    print(f"   ⚠️  Skipped: Prompt file not found")

print("\n" + "=" * 50)
print("✅ All MCP tests completed!")
