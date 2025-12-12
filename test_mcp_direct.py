#!/usr/bin/env python3
import subprocess
import json
import os

print("🧪 Testing MCP Functionality (Direct)")
print("=" * 50)

# Test 1: GPU Status via curl
print("\n1. Testing GPU Status...")
result = subprocess.run(
    ['curl', '-s', 'http://0.0.0.0:8080/api/gpu/status'],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
print(f"   Result: {data}")
assert 'loaded' in data, "Should have 'loaded' field"
print("   ✅ PASSED")

# Test 2: GPU Offload via curl
print("\n2. Testing GPU Offload...")
result = subprocess.run(
    ['curl', '-s', '-X', 'POST', 'http://0.0.0.0:8080/api/gpu/offload'],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
print(f"   Result: {data}")
assert 'status' in data, "Should have 'status' field"
print("   ✅ PASSED")

# Test 3: TTS via curl (MCP would use this)
print("\n3. Testing TTS API (as MCP would)...")
prompt_path = '/home/neo/upload/GLM-TTS/examples/prompt/jiayan_en1.wav'
output_path = '/home/neo/upload/GLM-TTS/outputs/mcp_direct_test.wav'

if os.path.exists(prompt_path):
    cmd = [
        'curl', '-s', '-X', 'POST', 'http://0.0.0.0:8080/api/tts',
        '-F', 'text=MCP功能测试',
        '-F', f'prompt_audio=@{prompt_path}',
        '-F', 'prompt_text=测试',
        '-o', output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"   Output: {output_path}")
        print(f"   Size: {os.path.getsize(output_path)} bytes")
        print("   ✅ PASSED")
    else:
        print("   ❌ FAILED: No output file")
else:
    print("   ⚠️  Skipped: Prompt file not found")

# Test 4: Check MCP server can start
print("\n4. Testing MCP Server Startup...")
result = subprocess.run(
    ['python3', 'mcp_server.py', '--help'],
    capture_output=True, text=True, timeout=5
)
if 'FastMCP' in result.stderr or result.returncode == 0:
    print("   MCP server script is valid")
    print("   ✅ PASSED")
else:
    print(f"   Output: {result.stdout}")
    print(f"   Error: {result.stderr}")

print("\n" + "=" * 50)
print("✅ All MCP functionality tests completed!")
print("\nNote: MCP tools work by calling the API endpoints.")
print("To use MCP in Claude/Cline, configure mcp_config.json")
