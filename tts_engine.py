import os
import torch
import torchaudio
import whisper
from voice_cache import VoiceCacheManager
from cosyvoice.cli.frontend import TTSFrontEnd, SpeechTokenizer, TextFrontEnd
from utils import yaml_util, tts_model_util
from utils.audio import mel_spectrogram
from transformers import AutoTokenizer, LlamaForCausalLM
from llm.glmtts import GLMTTS
from functools import partial

MAX_LLM_SEQ_INP_LEN = 750

class TTSEngine:
    def __init__(self, ckpt_dir="./ckpt", enable_memory_cache=True):
        self.ckpt_dir = ckpt_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.whisper_model = None
        self.voice_cache = VoiceCacheManager(enable_memory_cache=enable_memory_cache)
        
        # GLM-TTS models
        self.frontend = None
        self.text_frontend = None
        self.speech_tokenizer = None
        self.llm = None
        self.token2wav = None
        self.special_token_ids = None
        self.models_loaded = False
        
        print(f"[TTS] Voice cache initialized: {self.voice_cache.get_cache_stats()}")
        
    def load_glm_models(self, sample_rate=24000, use_phoneme=False):
        """Load all GLM-TTS models to GPU"""
        if self.models_loaded:
            return
            
        print("[TTS] Loading GLM-TTS models...")
        
        # Load Speech Tokenizer
        _model, _feature_extractor = yaml_util.load_speech_tokenizer("ckpt/speech_tokenizer")
        self.speech_tokenizer = SpeechTokenizer(_model, _feature_extractor)
        
        # Load Frontends
        if sample_rate == 24000:
            feat_extractor = partial(mel_spectrogram, sampling_rate=sample_rate, hop_size=480, 
                                    n_fft=1920, num_mels=80, win_size=1920, fmin=0, fmax=8000, center=False)
        else:
            raise ValueError(f"Unsupported sample_rate: {sample_rate}")
            
        glm_tokenizer = AutoTokenizer.from_pretrained("ckpt/vq32k-phoneme-tokenizer", trust_remote_code=True)
        tokenize_fn = lambda text: glm_tokenizer.encode(text)
        
        self.frontend = TTSFrontEnd(
            tokenize_fn,
            self.speech_tokenizer,
            feat_extractor,
            os.path.join("./frontend", "campplus.onnx"),
            os.path.join("./frontend", "spk2info.pt"),
            self.device,
        )
        self.text_frontend = TextFrontEnd(use_phoneme)
        
        # Load LLM
        llama_path = "ckpt/llm"
        self.llm = GLMTTS(llama_cfg_path=os.path.join(llama_path, "config.json"), mode="PRETRAIN")
        self.llm.llama = LlamaForCausalLM.from_pretrained(llama_path, dtype=torch.float32).to(self.device)
        self.llm.llama_embedding = self.llm.llama.model.embed_tokens
        
        self.special_token_ids = self._get_special_token_ids(tokenize_fn)
        self.llm.set_runtime_vars(special_token_ids=self.special_token_ids)
        
        # Load Flow and wrap with Token2Wav
        flow = yaml_util.load_flow_model("ckpt/flow/flow.pt", "ckpt/flow/config.yaml", self.device)
        self.token2wav = tts_model_util.Token2Wav(flow, sample_rate=sample_rate, device=self.device)
        
        self.models_loaded = True
        print("[TTS] ✓ GLM-TTS models loaded to GPU")
        
    def _get_special_token_ids(self, tokenize_fn):
        """Get special token IDs"""
        _special_token_ids = {
            "ats": "<|audio_0|>",
            "ate": "<|audio_32767|>",
            "boa": "<|begin_of_audio|>",
            "eoa": "<|user|>",
            "pad": "<|endoftext|>",
        }
        special_token_ids = {}
        endoftext_id = tokenize_fn("<|endoftext|>")[0]
        for k, v in _special_token_ids.items():
            __ids = tokenize_fn(v)
            if len(__ids) != 1 or __ids[0] < endoftext_id:
                raise AssertionError(f"Invalid special token: {k}")
            special_token_ids[k] = __ids[0]
        return special_token_ids
    
    def load_whisper(self):
        """Lazy load Whisper model"""
        if self.whisper_model is None:
            print("[Whisper] Loading model...")
            self.whisper_model = whisper.load_model("base", device="cuda")
            print("[Whisper] Model loaded")
        return self.whisper_model
        
    def transcribe_audio(self, audio_path):
        """Transcribe audio using Whisper"""
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
    
    def _llm_forward(self, prompt_text_token, tts_text_token, prompt_speech_token):
        """Single LLM forward pass"""
        def _assert_shape_and_get_len(token):
            assert token.ndim == 2 and token.shape[0] == 1
            return torch.tensor([token.shape[1]], dtype=torch.int32).to(token.device)
        
        prompt_text_token_len = _assert_shape_and_get_len(prompt_text_token)
        tts_text_token_len = _assert_shape_and_get_len(tts_text_token)
        prompt_speech_token_len = _assert_shape_and_get_len(prompt_speech_token)
        
        tts_speech_token = self.llm.inference(
            text=tts_text_token,
            text_len=tts_text_token_len,
            prompt_text=prompt_text_token,
            prompt_text_len=prompt_text_token_len,
            prompt_speech_token=prompt_speech_token,
            prompt_speech_token_len=prompt_speech_token_len,
            beam_size=1,
            sampling=25,
            sample_method="ras",
            spk=None,
        )
        return tts_speech_token[0].tolist()
    
    def _flow_forward(self, token_list, prompt_speech_tokens, speech_feat, embedding):
        """Single Flow forward pass"""
        wav, full_mel = self.token2wav.token2wav_with_cache(
            token_list,
            prompt_token=prompt_speech_tokens,
            prompt_feat=speech_feat,
            embedding=embedding,
        )
        return wav.detach().cpu(), full_mel
    
    def generate(self, text, prompt_audio, prompt_text, output_path="output.wav", sample_rate=24000, skip_whisper=False):
        """Generate speech using loaded models"""
        if not self.models_loaded:
            self.load_glm_models(sample_rate=sample_rate)
        
        # Auto-transcribe if prompt_text is empty and skip_whisper is False
        if not prompt_text:
            if skip_whisper:
                raise ValueError("prompt_text is required when skip_whisper=True")
            print("[TTS] prompt_text is empty, using Whisper to transcribe...")
            prompt_text = self.transcribe_audio(prompt_audio)
            if not prompt_text:
                raise ValueError("Whisper transcription failed and no prompt_text provided")
        
        # Text normalization
        prompt_text_norm = self.text_frontend.text_normalize(prompt_text + " ")
        synth_text_norm = self.text_frontend.text_normalize(text)
        
        # Extract features
        prompt_text_token = self.frontend._extract_text_token(prompt_text_norm)
        prompt_speech_token = self.frontend._extract_speech_token([prompt_audio])
        speech_feat = self.frontend._extract_speech_feat(prompt_audio, sample_rate=sample_rate)
        embedding = self.frontend._extract_spk_embedding(prompt_audio)
        
        # Prepare tokens
        cache_speech_token = [prompt_speech_token.squeeze().tolist()]
        flow_prompt_token = torch.tensor(cache_speech_token, dtype=torch.int32).to(self.device)
        
        # Normalize and process text
        tts_text_tn = self.text_frontend.text_normalize(text)
        
        outputs = []
        for tts_text_tn in [tts_text_tn]:
            tts_text_token = self.frontend._extract_text_token(tts_text_tn + " ")
            
            # LLM inference
            token_list_res = self._llm_forward(
                prompt_text_token=prompt_text_token,
                tts_text_token=tts_text_token,
                prompt_speech_token=prompt_speech_token
            )
            
            # Flow inference
            output, _ = self._flow_forward(
                token_list=token_list_res,
                prompt_speech_tokens=flow_prompt_token,
                speech_feat=speech_feat,
                embedding=embedding
            )
            outputs.append(output)
        
        # Concatenate outputs
        tts_speech = torch.concat(outputs, dim=1)
        
        # Save audio
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        torchaudio.save(output_path, tts_speech, sample_rate)
        
        return output_path
    
    def generate_with_voice_id(self, text, voice_id, output_path="output.wav"):
        """Generate speech using cached voice ID"""
        cached_voice = self.voice_cache.load_voice(voice_id)
        if not cached_voice:
            raise ValueError(f"Voice ID not found: {voice_id}")
        
        cached_audio_path = self.voice_cache.get_audio_path(voice_id)
        if not cached_audio_path:
            raise ValueError(f"Audio file not found for voice ID: {voice_id}")
        
        return self.generate(
            text=text,
            prompt_audio=cached_audio_path,
            prompt_text=cached_voice["prompt_text"],
            output_path=output_path
        )
    
    def preload_models(self):
        """Preload all models to GPU"""
        print("[TTS] Preloading models to GPU...")
        self.load_whisper()
        print("[TTS] ✓ Whisper model loaded")
        self.load_glm_models()
        print("[TTS] ✓ All models preloaded to GPU")
    
    def offload_models(self):
        """Offload models from GPU"""
        print("[TTS] Offloading models from GPU...")
        if self.whisper_model:
            del self.whisper_model
            self.whisper_model = None
        if self.llm:
            del self.llm
            self.llm = None
        if self.token2wav:
            del self.token2wav
            self.token2wav = None
        if self.frontend:
            del self.frontend
            self.frontend = None
        self.models_loaded = False
        torch.cuda.empty_cache()
        print("[TTS] ✓ Models offloaded")
    
    def get_gpu_memory_usage(self):
        """Get current GPU memory usage"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            return {
                "allocated_gb": round(allocated, 2),
                "reserved_gb": round(reserved, 2),
                "models_loaded": self.models_loaded
            }
        return {"error": "CUDA not available"}
