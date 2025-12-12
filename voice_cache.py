"""
Voice Cache Manager - 语音特征缓存管理
支持文件系统和内存双层缓存
"""
import os
import json
import hashlib
import torch
import shutil
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class VoiceCacheManager:
    """语音缓存管理器"""
    
    def __init__(self, cache_dir: str = "/tmp/glm-tts-voices/voice_cache", 
                 enable_memory_cache: bool = True):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            enable_memory_cache: 是否启用内存缓存
        """
        self.cache_dir = cache_dir
        self.enable_memory_cache = enable_memory_cache
        self.memory_cache: Dict = {}
        
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"VoiceCacheManager initialized: cache_dir={cache_dir}, memory_cache={enable_memory_cache}")
        
        # 启动时加载所有缓存到内存
        if self.enable_memory_cache:
            self._load_all_to_memory()
    
    def generate_voice_id(self, audio_path: str) -> str:
        """
        生成语音ID（基于音频文件MD5）
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            voice_id: 8位短ID
        """
        with open(audio_path, 'rb') as f:
            audio_hash = hashlib.md5(f.read()).hexdigest()
        return audio_hash[:8]  # 使用前8位作为ID
    
    def save_voice(self, voice_id: str, audio_path: str, prompt_text: str,
                   text_token: torch.Tensor, speech_token: torch.Tensor,
                   speech_feat: torch.Tensor, embedding: torch.Tensor,
                   sample_rate: int = 24000) -> Dict:
        """
        保存语音特征到缓存
        
        Args:
            voice_id: 语音ID
            audio_path: 原始音频路径
            prompt_text: 参考文本
            text_token: 文本Token
            speech_token: 语音Token
            speech_feat: Mel特征
            embedding: 说话人嵌入
            sample_rate: 采样率
            
        Returns:
            metadata: 元数据字典
        """
        voice_dir = os.path.join(self.cache_dir, voice_id)
        os.makedirs(voice_dir, exist_ok=True)
        
        # 保存音频文件
        audio_ext = os.path.splitext(audio_path)[1]
        cached_audio_path = os.path.join(voice_dir, f"reference{audio_ext}")
        shutil.copy2(audio_path, cached_audio_path)
        
        # 保存特征
        torch.save(text_token, os.path.join(voice_dir, "text_token.pt"))
        torch.save(speech_token, os.path.join(voice_dir, "speech_token.pt"))
        torch.save(speech_feat, os.path.join(voice_dir, "speech_feat.pt"))
        torch.save(embedding, os.path.join(voice_dir, "embedding.pt"))
        
        # 保存元数据
        metadata = {
            "voice_id": voice_id,
            "prompt_text": prompt_text,
            "sample_rate": sample_rate,
            "audio_file": f"reference{audio_ext}",
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        }
        
        with open(os.path.join(voice_dir, "metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # 保存到内存缓存
        if self.enable_memory_cache:
            self.memory_cache[voice_id] = {
                "text_token": text_token,
                "speech_token": speech_token,
                "speech_feat": speech_feat,
                "embedding": embedding,
                "metadata": metadata
            }
        
        logger.info(f"Voice cached: {voice_id} - {prompt_text[:20]}...")
        return metadata
    
    def load_voice(self, voice_id: str) -> Optional[Dict]:
        """
        加载语音特征
        
        Args:
            voice_id: 语音ID
            
        Returns:
            features: 特征字典，包含所有缓存的数据
        """
        # 优先从内存加载
        if self.enable_memory_cache and voice_id in self.memory_cache:
            logger.info(f"Voice loaded from memory: {voice_id}")
            self._update_last_used(voice_id)
            return self.memory_cache[voice_id]
        
        # 从文件系统加载
        voice_dir = os.path.join(self.cache_dir, voice_id)
        if not os.path.exists(voice_dir):
            logger.warning(f"Voice not found: {voice_id}")
            return None
        
        try:
            # 加载元数据
            with open(os.path.join(voice_dir, "metadata.json"), 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 加载特征
            features = {
                "text_token": torch.load(os.path.join(voice_dir, "text_token.pt")),
                "speech_token": torch.load(os.path.join(voice_dir, "speech_token.pt")),
                "speech_feat": torch.load(os.path.join(voice_dir, "speech_feat.pt")),
                "embedding": torch.load(os.path.join(voice_dir, "embedding.pt")),
                "metadata": metadata
            }
            
            # 保存到内存缓存
            if self.enable_memory_cache:
                self.memory_cache[voice_id] = features
            
            self._update_last_used(voice_id)
            logger.info(f"Voice loaded from disk: {voice_id}")
            return features
            
        except Exception as e:
            logger.error(f"Failed to load voice {voice_id}: {e}")
            return None
    
    def list_voices(self) -> List[Dict]:
        """
        列出所有缓存的语音
        
        Returns:
            voices: 语音列表
        """
        voices = []
        
        if not os.path.exists(self.cache_dir):
            return voices
        
        for voice_id in os.listdir(self.cache_dir):
            voice_dir = os.path.join(self.cache_dir, voice_id)
            if not os.path.isdir(voice_dir):
                continue
            
            metadata_path = os.path.join(voice_dir, "metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    voices.append(metadata)
                except Exception as e:
                    logger.error(f"Failed to read metadata for {voice_id}: {e}")
        
        # 按最后使用时间排序
        voices.sort(key=lambda x: x.get('last_used', ''), reverse=True)
        return voices
    
    def delete_voice(self, voice_id: str) -> bool:
        """
        删除语音缓存
        
        Args:
            voice_id: 语音ID
            
        Returns:
            success: 是否成功
        """
        voice_dir = os.path.join(self.cache_dir, voice_id)
        
        if not os.path.exists(voice_dir):
            logger.warning(f"Voice not found: {voice_id}")
            return False
        
        try:
            shutil.rmtree(voice_dir)
            
            # 从内存缓存删除
            if voice_id in self.memory_cache:
                del self.memory_cache[voice_id]
            
            logger.info(f"Voice deleted: {voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete voice {voice_id}: {e}")
            return False
    
    def exists(self, voice_id: str) -> bool:
        """
        检查语音是否存在
        
        Args:
            voice_id: 语音ID
            
        Returns:
            exists: 是否存在
        """
        if self.enable_memory_cache and voice_id in self.memory_cache:
            return True
        
        voice_dir = os.path.join(self.cache_dir, voice_id)
        return os.path.exists(voice_dir)
    
    def get_audio_path(self, voice_id: str) -> Optional[str]:
        """
        获取缓存的音频文件路径
        
        Args:
            voice_id: 语音ID
            
        Returns:
            audio_path: 音频文件路径
        """
        voice_dir = os.path.join(self.cache_dir, voice_id)
        if not os.path.exists(voice_dir):
            return None
        
        metadata_path = os.path.join(voice_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            audio_file = metadata.get('audio_file', 'reference.wav')
            return os.path.join(voice_dir, audio_file)
        except:
            return None
    
    def _update_last_used(self, voice_id: str):
        """更新最后使用时间"""
        voice_dir = os.path.join(self.cache_dir, voice_id)
        metadata_path = os.path.join(voice_dir, "metadata.json")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata['last_used'] = datetime.now().isoformat()
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Failed to update last_used for {voice_id}: {e}")
    
    def _load_all_to_memory(self):
        """启动时加载所有缓存到内存"""
        logger.info("Loading all voice caches to memory...")
        voices = self.list_voices()
        
        for voice_meta in voices:
            voice_id = voice_meta['voice_id']
            if voice_id not in self.memory_cache:
                self.load_voice(voice_id)
        
        logger.info(f"Loaded {len(self.memory_cache)} voices to memory")
    
    def clear_memory_cache(self):
        """清空内存缓存"""
        self.memory_cache.clear()
        logger.info("Memory cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        voices = self.list_voices()
        
        total_size = 0
        for voice_id in os.listdir(self.cache_dir):
            voice_dir = os.path.join(self.cache_dir, voice_id)
            if os.path.isdir(voice_dir):
                for root, dirs, files in os.walk(voice_dir):
                    total_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)
        
        return {
            "total_voices": len(voices),
            "memory_cached": len(self.memory_cache),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "cache_dir": self.cache_dir,
            "memory_cache_enabled": self.enable_memory_cache
        }
