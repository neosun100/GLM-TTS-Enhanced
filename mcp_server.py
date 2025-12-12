#!/usr/bin/env python3
import os
import sys
import subprocess
from fastmcp import FastMCP

mcp = FastMCP("GLM-TTS")

@mcp.tool()
def text_to_speech(
    text: str,
    prompt_audio_path: str,
    output_path: str,
    prompt_text: str = ""
) -> dict:
    """
    文本转语音
    
    Args:
        text: 要合成的文本
        prompt_audio_path: 参考音频文件路径
        output_path: 输出音频文件路径
        prompt_text: 参考音频对应的文本（可选）
    
    Returns:
        包含状态和输出路径的字典
    """
    try:
        # Call API
        cmd = [
            'curl', '-s', '-X', 'POST', 'http://0.0.0.0:8080/api/tts',
            '-F', f'text={text}',
            '-F', f'prompt_audio=@{prompt_audio_path}',
            '-F', f'prompt_text={prompt_text}',
            '-o', output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return {'status': 'success', 'output': output_path}
        else:
            return {'status': 'error', 'error': result.stderr or 'Unknown error'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

@mcp.tool()
def get_gpu_status() -> dict:
    """
    获取 GPU 状态
    
    Returns:
        GPU 状态信息
    """
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://0.0.0.0:8080/api/gpu/status'],
            capture_output=True, text=True
        )
        import json
        return json.loads(result.stdout)
    except Exception as e:
        return {'error': str(e)}

@mcp.tool()
def offload_gpu() -> dict:
    """
    释放 GPU 显存
    
    Returns:
        操作状态
    """
    try:
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', 'http://0.0.0.0:8080/api/gpu/offload'],
            capture_output=True, text=True
        )
        import json
        return json.loads(result.stdout)
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    mcp.run()
