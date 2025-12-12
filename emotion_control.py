"""
情感控制模块 - GLM-TTS v1.2.0
支持情感强度调节和预设情感类型
"""
import json
from typing import Dict, Optional

class EmotionController:
    """情感控制器"""
    
    EMOTION_PRESETS = {
        'neutral': {'intensity': 0.0, 'description': '中性，无情感倾向'},
        'happy': {'intensity': 0.7, 'description': '快乐，积极向上'},
        'sad': {'intensity': 0.6, 'description': '悲伤，低沉'},
        'angry': {'intensity': 0.8, 'description': '愤怒，激烈'},
        'excited': {'intensity': 0.9, 'description': '兴奋，高昂'}
    }
    
    def __init__(self):
        self.current_emotion = 'neutral'
        self.current_intensity = 0.0
    
    def set_emotion(self, emotion_type: str, intensity: Optional[float] = None) -> Dict:
        """设置情感类型和强度"""
        if emotion_type not in self.EMOTION_PRESETS:
            raise ValueError(f"不支持的情感类型: {emotion_type}")
        
        preset = self.EMOTION_PRESETS[emotion_type]
        self.current_emotion = emotion_type
        self.current_intensity = intensity if intensity is not None else preset['intensity']
        
        # 限制范围
        self.current_intensity = max(0.0, min(1.0, self.current_intensity))
        
        return {
            'emotion': self.current_emotion,
            'intensity': self.current_intensity,
            'description': preset['description']
        }
    
    def get_emotion_params(self) -> Dict:
        """获取当前情感参数（用于TTS生成）"""
        return {
            'emotion_type': self.current_emotion,
            'emotion_intensity': self.current_intensity,
            'exaggeration': self.current_intensity  # GRPO参数
        }
    
    def reset(self):
        """重置为中性"""
        self.current_emotion = 'neutral'
        self.current_intensity = 0.0
    
    @staticmethod
    def list_emotions() -> Dict:
        """列出所有支持的情感类型"""
        return EmotionController.EMOTION_PRESETS
