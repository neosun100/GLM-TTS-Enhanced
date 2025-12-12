"""
流式推理引擎 - GLM-TTS v1.2.0
支持实时音频流式生成和SSE推送
"""
import queue
import threading
from typing import Generator, Optional, Callable
import time

class StreamingEngine:
    """流式推理引擎"""
    
    def __init__(self, chunk_duration=1.0):
        """
        Args:
            chunk_duration: 每个音频块的时长（秒）
        """
        self.chunk_duration = chunk_duration
        self.audio_queue = queue.Queue()
        self.is_generating = False
        
    def generate_stream(self, tts_engine, text: str, voice_id: str, 
                       emotion_params: dict = None) -> Generator[bytes, None, None]:
        """
        流式生成音频
        
        Args:
            tts_engine: TTS引擎实例
            text: 要合成的文本
            voice_id: 语音ID
            emotion_params: 情感参数
            
        Yields:
            bytes: 音频数据块
        """
        self.is_generating = True
        
        try:
            # 分句处理
            sentences = self._split_text(text)
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                # 生成单句音频
                chunk_data = self._generate_chunk(
                    tts_engine, sentence, voice_id, emotion_params
                )
                
                # 推送进度
                progress = {
                    'type': 'chunk',
                    'index': i,
                    'total': len(sentences),
                    'text': sentence,
                    'size': len(chunk_data)
                }
                
                yield self._format_sse(progress, chunk_data)
                
        finally:
            self.is_generating = False
            yield self._format_sse({'type': 'done'}, None)
    
    def _split_text(self, text: str) -> list:
        """分句（按标点符号）"""
        import re
        sentences = re.split(r'[。！？；\n.!?;]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _generate_chunk(self, tts_engine, text: str, voice_id: str, 
                       emotion_params: dict) -> bytes:
        """生成单个音频块"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # 调用TTS引擎生成
            tts_engine.generate_with_voice_id(
                text=text,
                voice_id=voice_id,
                output_path=tmp_path,
                **emotion_params
            )
            
            # 读取音频数据
            with open(tmp_path, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def _format_sse(self, metadata: dict, audio_data: Optional[bytes]) -> str:
        """格式化SSE消息"""
        import json
        import base64
        
        message = {
            'metadata': metadata,
            'audio': base64.b64encode(audio_data).decode() if audio_data else None
        }
        
        return f"data: {json.dumps(message)}\n\n"
    
    def stop(self):
        """停止生成"""
        self.is_generating = False
