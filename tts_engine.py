import os
import subprocess
import json
import tempfile
import shutil
import time
import whisper
from voice_cache import VoiceCacheManager

class TTSEngine:
    def __init__(self, ckpt_dir="./ckpt", enable_memory_cache=True):
        self.ckpt_dir = ckpt_dir
        self.whisper_model = None
        self.voice_cache = VoiceCacheManager(enable_memory_cache=enable_memory_cache)
        print(f"[TTS] Voice cache initialized: {self.voice_cache.get_cache_stats()}")
        
    def load_whisper(self):
        """延迟加载Whisper模型"""
        if self.whisper_model is None:
            print("[Whisper] Loading model...")
            self.whisper_model = whisper.load_model("base", device="cuda")
            print("[Whisper] Model loaded")
        return self.whisper_model
        
    def transcribe_audio(self, audio_path):
        """使用Whisper转录音频"""
        try:
            model = self.load_whisper()
            print(f"[Whisper] Transcribing {audio_path}...")
            result = model.transcribe(audio_path, language="zh")
            text = result["text"].strip()
            print(f"[Whisper] Transcribed: {text}")
            return text
        except Exception as e:
            print(f"[Whisper] Error: {e}")
            return ""
    
    def generate_with_voice_id(self, text, voice_id, output_path="output.wav",
                               progress_callback=None, temperature=0.8, top_p=0.9, 
                               sampling_strategy='balanced', emotion_type='neutral',
                               emotion_intensity=0.0, exaggeration=0.0):
        """
        使用缓存的语音ID生成语音（快速模式）
        
        Args:
            text: 要合成的文本
            voice_id: 语音ID
            output_path: 输出路径
            progress_callback: 进度回调
            temperature: 温度参数
            top_p: Top-p参数
            emotion_type: 情感类型
            emotion_intensity: 情感强度(0.0-1.0)
            exaggeration: GRPO情感夸张参数(0.0-1.0)
            sampling_strategy: 采样策略
            
        Returns:
            output_path: 生成的音频路径
            voice_id: 使用的语音ID
        """
        start_time = time.time()
        
        # 从缓存加载语音特征
        if progress_callback:
            progress_callback(f"加载语音缓存 (ID: {voice_id})", time.time() - start_time)
        
        cached_voice = self.voice_cache.load_voice(voice_id)
        if not cached_voice:
            raise ValueError(f"Voice ID not found: {voice_id}")
        
        # 获取缓存的音频路径
        cached_audio_path = self.voice_cache.get_audio_path(voice_id)
        if not cached_audio_path:
            raise ValueError(f"Cached audio not found for voice ID: {voice_id}")
        
        # 获取缓存的参考文本
        prompt_text = cached_voice['metadata']['prompt_text']
        
        print(f"[TTS] Using cached voice: {voice_id} - {prompt_text[:30]}...")
        
        # 使用缓存的音频路径生成
        return self.generate(
            text=text,
            prompt_audio_path=cached_audio_path,
            prompt_text=prompt_text,
            output_path=output_path,
            progress_callback=progress_callback,
            skip_whisper=True,  # 已有缓存，跳过Whisper
            temperature=temperature,
            top_p=top_p,
            sampling_strategy=sampling_strategy,
            voice_id=voice_id  # 传递voice_id，避免重复缓存
        )
        
    def generate(self, text, prompt_audio_path, prompt_text="", output_path="output.wav", 
                 progress_callback=None, skip_whisper=False, temperature=0.8, top_p=0.9, 
                 sampling_strategy='balanced', voice_id=None):
        """
        使用官方推理脚本生成语音
        
        Args:
            text: 要合成的文本
            prompt_audio_path: 参考音频路径
            prompt_text: 参考文本（可选）
            output_path: 输出路径
            progress_callback: 进度回调
            skip_whisper: 是否跳过Whisper
            temperature: 温度参数
            top_p: Top-p参数
            sampling_strategy: 采样策略
            voice_id: 语音ID（如果已知，避免重复缓存）
            
        Returns:
            output_path: 生成的音频路径
            voice_id: 语音ID（新生成或已存在）
        """
        start_time = time.time()
        exp_name = f"api_{int(time.time())}"
        
        # 生成或获取voice_id
        if not voice_id:
            voice_id = self.voice_cache.generate_voice_id(prompt_audio_path)
        
        # 检查是否已缓存
        is_cached = self.voice_cache.exists(voice_id)
        
        # 如果没有提供参考文本且未跳过Whisper，使用Whisper自动转录
        if not prompt_text or prompt_text.strip() == "":
            if not skip_whisper:
                if progress_callback:
                    progress_callback("正在识别参考音频内容 (Whisper)", time.time() - start_time)
                print("[TTS] Using Whisper to transcribe...")
                prompt_text = self.transcribe_audio(prompt_audio_path)
                if not prompt_text:
                    print("[TTS] Warning: Whisper transcription failed")
                    prompt_text = "参考音频"  # 默认文本
            else:
                print("[TTS] Skipped Whisper as requested")
                prompt_text = "参考音频"
        
        if progress_callback:
            progress_callback("准备推理数据", time.time() - start_time)
        
        # 根据采样策略调整参数
        if sampling_strategy == 'fast':
            max_tokens = 1500
            do_sample = True
        elif sampling_strategy == 'quality':
            max_tokens = 2500
            do_sample = True
        else:  # balanced
            max_tokens = 2000
            do_sample = True
        
        # 在examples目录创建临时jsonl
        jsonl_name = f"{exp_name}.jsonl"
        jsonl_path = os.path.join("/app/examples", jsonl_name)
        
        with open(jsonl_path, 'w') as f:
            data = {
                "uttid": "0",
                "syn_text": text,
                "prompt_text": prompt_text,
                "prompt_speech": prompt_audio_path
            }
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        try:
            if progress_callback:
                status_msg = f"生成语音 ({sampling_strategy}模式)"
                if is_cached:
                    status_msg += " [使用缓存特征]"
                progress_callback(status_msg, time.time() - start_time)
            
            # 调用官方推理脚本
            cmd = [
                'python3', 'glmtts_inference.py',
                f'--data={exp_name}',
                f'--exp_name={exp_name}',
                '--use_cache'
            ]
            
            result = subprocess.run(
                cmd,
                cwd='/app',
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"Inference failed: {result.stderr}")
            
            if progress_callback:
                progress_callback("处理输出文件", time.time() - start_time)
            
            # 查找生成的音频文件
            output_dir = f'/app/outputs/pretrain{exp_name}/{exp_name}'
            if os.path.exists(output_dir):
                files = [f for f in os.listdir(output_dir) if f.endswith('.wav')]
                if files:
                    source_file = os.path.join(output_dir, files[0])
                    shutil.copy(source_file, output_path)
                    # 清理临时文件
                    shutil.rmtree(f'/app/outputs/pretrain{exp_name}', ignore_errors=True)
                    os.remove(jsonl_path)
                    
                    elapsed = time.time() - start_time
                    if progress_callback:
                        progress_callback(f"完成！耗时 {elapsed:.1f}秒", elapsed)
                    
                    print(f"[TTS] Generated: {output_path} (voice_id: {voice_id}, cached: {is_cached})")
                    return output_path, voice_id
            
            raise Exception("Output file not found")
            
        except Exception as e:
            # 清理
            if os.path.exists(jsonl_path):
                os.remove(jsonl_path)
            shutil.rmtree(f'/app/outputs/pretrain{exp_name}', ignore_errors=True)
            raise e
    
    def cache_voice_from_audio(self, audio_path, prompt_text="", skip_whisper=False):
        """
        从音频文件创建语音缓存
        
        Args:
            audio_path: 音频文件路径
            prompt_text: 参考文本（可选）
            skip_whisper: 是否跳过Whisper
            
        Returns:
            voice_id: 生成的语音ID
            metadata: 元数据
        """
        # 生成voice_id
        voice_id = self.voice_cache.generate_voice_id(audio_path)
        
        # 检查是否已存在
        if self.voice_cache.exists(voice_id):
            print(f"[TTS] Voice already cached: {voice_id}")
            cached_voice = self.voice_cache.load_voice(voice_id)
            return voice_id, cached_voice['metadata']
        
        # 获取参考文本
        if not prompt_text or prompt_text.strip() == "":
            if not skip_whisper:
                print("[TTS] Transcribing audio for cache...")
                prompt_text = self.transcribe_audio(audio_path)
                if not prompt_text:
                    prompt_text = "参考音频"
            else:
                prompt_text = "参考音频"
        
        print(f"[TTS] Caching voice: {voice_id} - {prompt_text[:30]}...")
        
        # TODO: 这里需要实际提取特征并保存
        # 当前简化实现：只保存音频和元数据
        # 实际应该调用frontend提取text_token, speech_token, speech_feat, embedding
        
        # 临时实现：创建占位符
        import torch
        text_token = torch.zeros(1, 10)
        speech_token = torch.zeros(1, 100)
        speech_feat = torch.zeros(1, 80, 100)
        embedding = torch.zeros(1, 192)
        
        metadata = self.voice_cache.save_voice(
            voice_id=voice_id,
            audio_path=audio_path,
            prompt_text=prompt_text,
            text_token=text_token,
            speech_token=speech_token,
            speech_feat=speech_feat,
            embedding=embedding
        )
        
        return voice_id, metadata
    
    def list_cached_voices(self):
        """列出所有缓存的语音"""
        return self.voice_cache.list_voices()
    
    def delete_cached_voice(self, voice_id):
        """删除缓存的语音"""
        return self.voice_cache.delete_voice(voice_id)
    
    def get_cache_stats(self):
        """获取缓存统计信息"""
        return self.voice_cache.get_cache_stats()
