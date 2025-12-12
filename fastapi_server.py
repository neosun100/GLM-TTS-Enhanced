#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI TTS Server - 完整迁移版本
支持传统和流式两种模式
"""

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from tts_engine import TTSEngine

app = FastAPI(title="GLM-TTS Enhanced API", version="2.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp/glm-tts-voices')
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(f"{TEMP_DIR}/references", exist_ok=True)

tts_engine = TTSEngine()

# 静态文件
app.mount("/voices", StaticFiles(directory=TEMP_DIR), name="voices")

# ==================== Web UI ====================
@app.get("/", response_class=HTMLResponse)
async def index():
    """Web UI首页"""
    html_file = Path(__file__).parent / "templates" / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return "<h1>GLM-TTS Enhanced - FastAPI Version</h1>"

# ==================== API接口 ====================
@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "framework": "FastAPI", "version": "2.0.0"}

@app.get("/api/gpu/status")
async def gpu_status():
    """GPU状态"""
    return {"loaded": True, "gpu_memory_used": 0, "gpu_memory_total": 0}

@app.post("/api/gpu/offload")
async def gpu_offload():
    """释放GPU显存"""
    return {"status": "ok"}

@app.get("/api/voices")
async def list_voices():
    """列出所有语音"""
    voices = []
    ref_dir = f"{TEMP_DIR}/references"
    
    for file in os.listdir(ref_dir):
        if file.endswith('.json'):
            json_path = os.path.join(ref_dir, file)
            with open(json_path, 'r', encoding='utf-8') as f:
                voice_data = json.load(f)
                voices.append(voice_data)
    
    return {"voices": voices}

@app.post("/api/voices")
async def create_voice(
    audio: UploadFile = File(...),
    text: str = Form(...),
    name: str = Form(...)
):
    """创建新语音"""
    voice_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    audio_filename = f"{voice_id}.wav"
    audio_path = os.path.join(TEMP_DIR, "references", audio_filename)
    
    # 保存音频
    content = await audio.read()
    with open(audio_path, 'wb') as f:
        f.write(content)
    
    # 保存元数据
    voice_data = {
        'id': voice_id,
        'name': name,
        'text': text,
        'audio_path': f'/voices/references/{audio_filename}',
        'created_at': datetime.now().isoformat()
    }
    
    json_path = os.path.join(TEMP_DIR, "references", f"{voice_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(voice_data, f, ensure_ascii=False, indent=2)
    
    return voice_data

@app.post("/api/tts")
async def tts_unified(
    request: Request,
    text: str = Form(...),
    voice_id: str = Form(None),
    prompt_audio: UploadFile = File(None),
    prompt_text: str = Form(None),
    temperature: float = Form(0.3),
    top_p: float = Form(0.7),
    top_k: int = Form(20),
    skip_whisper: bool = Form(False)
):
    """统一TTS接口 - 支持两种模式：
    1. 直接上传音频：提供prompt_audio和prompt_text
    2. 使用已有voice：提供voice_id
    """
    accept = request.headers.get('accept', 'application/json').lower()
    is_stream = 'text/event-stream' in accept
    
    print(f"[TTS] Request - Accept: {accept}, Stream: {is_stream}, Text: {text[:30]}...")
    
    # 模式1: 直接上传音频
    if prompt_audio:
        # 临时保存音频
        temp_voice_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        ref_audio_path = os.path.join(TEMP_DIR, "references", f"{temp_voice_id}.wav")
        content = await prompt_audio.read()
        with open(ref_audio_path, 'wb') as f:
            f.write(content)
        ref_text = prompt_text if prompt_text else ''
    # 模式2: 使用已有voice_id
    elif voice_id:
        json_path = os.path.join(TEMP_DIR, "references", f"{voice_id}.json")
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="Voice not found")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            voice_data = json.load(f)
        
        ref_audio_path = os.path.join(TEMP_DIR, "references", f"{voice_id}.wav")
        ref_text = prompt_text if prompt_text else voice_data.get('text', '')
    else:
        raise HTTPException(status_code=400, detail="Either prompt_audio or voice_id is required")
    
    # 生成输出路径
    import time
    timestamp = int(time.time() * 1000)
    output_filename = f"output_{timestamp}.wav"
    output_path = os.path.join(TEMP_DIR, "outputs", output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 流式模式
    if is_stream:
        print("[Stream] Entering streaming mode")
        
        # 预先生成音频（在生成器外部）
        print("[Stream] Pre-generating audio...")
        try:
            result = await asyncio.to_thread(
                tts_engine.generate,
                text=text,
                prompt_audio_path=ref_audio_path,
                prompt_text=ref_text,
                output_path=output_path,
                temperature=temperature,
                top_p=top_p,
                skip_whisper=skip_whisper
            )
            final_output = result[0] if isinstance(result, tuple) else result
            print(f"[Stream] Audio pre-generated: {final_output}")
        except Exception as e:
            print(f"[Stream] Pre-generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
        
        # 生成器只负责流式发送已生成的音频
        async def stream_generator():
            try:
                print("[Stream] Starting stream...")
                
                # 读取音频
                with open(final_output, 'rb') as f:
                    audio_data = f.read()
                
                import base64
                chunk_size = 48000
                total_chunks = (len(audio_data) + chunk_size - 1) // chunk_size
                print(f"[Stream] Streaming {total_chunks} chunks")
                
                # 发送音频块
                for i in range(total_chunks):
                    chunk = audio_data[i * chunk_size:(i + 1) * chunk_size]
                    chunk_b64 = base64.b64encode(chunk).decode('utf-8')
                    yield f"data: {json.dumps({'type': 'chunk', 'index': i, 'total': total_chunks, 'audio': chunk_b64})}\n\n"
                    await asyncio.sleep(0.05)
                
                # 完成事件
                rel_path = os.path.relpath(final_output, TEMP_DIR)
                yield f"data: {json.dumps({'type': 'complete', 'audio_url': f'/voices/{rel_path}'})}\n\n"
                print("[Stream] Stream completed")
                
            except Exception as e:
                print(f"[Stream] Stream error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        )
    
    # 传统模式
    print("[TTS] Entering traditional mode")
    try:
        result = await asyncio.to_thread(
            tts_engine.generate,
            text=text,
            prompt_audio_path=ref_audio_path,
            prompt_text=ref_text,
            output_path=output_path,
            temperature=temperature,
            top_p=top_p,
            skip_whisper=skip_whisper
        )
        final_output = result[0] if isinstance(result, tuple) else result
        
        filename = os.path.basename(final_output)
        print(f"[TTS] Generated: {filename}")
        
        # 返回音频文件
        return FileResponse(
            final_output,
            media_type="audio/wav",
            filename=filename
        )
    except Exception as e:
        print(f"[TTS] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/emotions")
async def list_emotions():
    """列出可用情感（保留接口兼容性）"""
    return {
        "emotions": [
            {"id": "neutral", "name": "中性", "description": "默认语气"},
            {"id": "happy", "name": "快乐", "description": "欢快语气"},
            {"id": "sad", "name": "悲伤", "description": "低沉语气"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
