"""
流式推理引擎 - GLM-TTS v1.2.0
支持实时音频流式生成和SSE推送
"""
import re
import tempfile
import os
import json
import base64

class StreamingEngine:
    """流式推理引擎"""
    
    def __init__(self, chunk_duration=1.0):
        self.chunk_duration = chunk_duration
        self.is_generating = False
        
    def generate_stream(self, tts_engine, text: str, voice_id: str, 
                       emotion_params: dict = None):
        """
        流式生成音频
        
        Args:
            tts_engine: TTS引擎实例
            text: 要合成的文本
            voice_id: 语音ID
            emotion_params: 情感参数
            
        Yields:
            str: SSE格式的消息
        """
        self.is_generating = True
        emotion_params = emotion_params or {}
        
        try:
            # 分句
            sentences = self._split_text(text)
            total = len(sentences)
            
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                
                # 生成音频块
                audio_data = self._generate_chunk(
                    tts_engine, sentence, voice_id, emotion_params
                )
                
                # 发送进度
                yield self._format_sse({
                    'type': 'chunk',
                    'index': i,
                    'total': total,
                    'text': sentence,
                    'size': len(audio_data)
                }, audio_data)
                
        except Exception as e:
            yield self._format_sse({'type': 'error', 'message': str(e)}, None)
        finally:
            self.is_generating = False
            yield self._format_sse({'type': 'done'}, None)
    
    def _split_text(self, text: str) -> list:
        """分句"""
        sentences = re.split(r'[。！？；\n.!?;]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _generate_chunk(self, tts_engine, text: str, voice_id: str, 
                       emotion_params: dict) -> bytes:
        """生成单个音频块"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            tts_engine.generate_with_voice_id(
                text=text,
                voice_id=voice_id,
                output_path=tmp_path,
                **emotion_params
            )
            
            with open(tmp_path, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def _format_sse(self, metadata: dict, audio_data: bytes = None) -> str:
        """格式化SSE消息"""
        message = {
            'metadata': metadata,
            'audio': base64.b64encode(audio_data).decode() if audio_data else None
        }
        return f"data: {json.dumps(message)}\n\n"
    
    def stop(self):
        """停止生成"""
        self.is_generating = False
