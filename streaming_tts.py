"""
流式TTS引擎 - GLM-TTS v1.3.0
使用原生token2wav_stream实现真正的流式输出
"""
import os
import subprocess
import json
import tempfile
import base64
import wave
import numpy as np
from typing import Generator

class StreamingTTSEngine:
    """流式TTS引擎，基于GLM-TTS原生token2wav_stream"""
    
    def __init__(self, tts_engine):
        self.tts_engine = tts_engine
        
    def generate_stream(self, text: str, voice_id: str) -> Generator[dict, None, None]:
        """
        流式生成语音
        
        Args:
            text: 要合成的文本
            voice_id: 语音ID
            
        Yields:
            dict: {'type': 'chunk'/'done', 'audio': base64_data, 'index': int}
        """
        # 获取voice cache
        voice_info = self.tts_engine.voice_cache.list_voices()
        voice_data = next((v for v in voice_info if v['voice_id'] == voice_id), None)
        
        if not voice_data:
            yield {'type': 'error', 'message': f'Voice ID not found: {voice_id}'}
            return
        
        # 使用临时文件生成，然后调用流式推理
        with tempfile.TemporaryDirectory() as tmpdir:
            # 准备输入
            input_json = os.path.join(tmpdir, 'input.json')
            ref_audio = voice_data['audio_path']
            
            # 创建输入JSON
            data = {
                "text": text,
                "prompt_audio": ref_audio,
                "prompt_text": voice_data.get('metadata', {}).get('reference_text', ''),
                "streaming": True  # 启用流式
            }
            
            with open(input_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            
            # 调用流式推理脚本
            cmd = [
                'python', 'glmtts_inference.py',
                '--data', tmpdir,
                '--exp_name', 'stream',
                '--use_cache', 'True',
                '--streaming'  # 流式参数
            ]
            
            try:
                # 启动进程
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                chunk_index = 0
                
                # 读取流式输出
                for line in process.stdout:
                    line_str = line.decode('utf-8').strip()
                    
                    if line_str.startswith('STREAM_CHUNK:'):
                        # 解析流式块
                        chunk_data = json.loads(line_str[13:])
                        
                        # 读取音频文件
                        chunk_file = chunk_data.get('file')
                        if chunk_file and os.path.exists(chunk_file):
                            with open(chunk_file, 'rb') as f:
                                audio_bytes = f.read()
                            
                            yield {
                                'type': 'chunk',
                                'index': chunk_index,
                                'audio': base64.b64encode(audio_bytes).decode(),
                                'duration': chunk_data.get('duration', 0)
                            }
                            
                            chunk_index += 1
                
                process.wait()
                
                if process.returncode == 0:
                    yield {'type': 'done', 'total_chunks': chunk_index}
                else:
                    error = process.stderr.read().decode('utf-8')
                    yield {'type': 'error', 'message': error}
                    
            except Exception as e:
                yield {'type': 'error', 'message': str(e)}
