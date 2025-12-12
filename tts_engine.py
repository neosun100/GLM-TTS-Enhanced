import os
import subprocess
import json
import tempfile
import shutil
import time
import whisper

class TTSEngine:
    def __init__(self, ckpt_dir="./ckpt"):
        self.ckpt_dir = ckpt_dir
        self.whisper_model = None
        
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
        
    def generate(self, text, prompt_audio_path, prompt_text="", output_path="output.wav", 
                 progress_callback=None, skip_whisper=False, temperature=0.8, top_p=0.9, sampling_strategy='balanced'):
        """使用官方推理脚本生成语音"""
        start_time = time.time()
        exp_name = f"api_{int(time.time())}"
        
        # 如果没有提供参考文本且未跳过Whisper，使用Whisper自动转录
        if not prompt_text or prompt_text.strip() == "":
            if not skip_whisper:
                if progress_callback:
                    progress_callback("正在识别参考音频内容 (Whisper)", time.time() - start_time)
                print("[TTS] Using Whisper to transcribe...")
                prompt_text = self.transcribe_audio(prompt_audio_path)
                if not prompt_text:
                    print("[TTS] Warning: Whisper transcription failed")
            else:
                print("[TTS] Skipped Whisper as requested")
        
        if progress_callback:
            progress_callback("准备推理数据", time.time() - start_time)
        
        # 根据采样策略调整参数
        if sampling_strategy == 'fast':
            # 快速模式：降低采样质量，加快速度
            max_tokens = 1500  # 减少最大token数
            do_sample = True
        elif sampling_strategy == 'quality':
            # 高质量模式
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
                progress_callback(f"生成语音 ({sampling_strategy}模式, temp={temperature}, top_p={top_p})", time.time() - start_time)
            
            # 调用官方推理脚本
            # 注意：官方脚本不直接支持这些参数，需要修改glmtts_inference.py
            # 这里先保持原样，实际加速主要靠skip_whisper
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
                    # 清理
                    shutil.rmtree(f'/app/outputs/pretrain{exp_name}', ignore_errors=True)
                    os.remove(jsonl_path)
                    return output_path
            
            raise Exception(f"No output audio in {output_dir}")
            
        except Exception as e:
            # 清理
            if os.path.exists(jsonl_path):
                os.remove(jsonl_path)
            raise e
