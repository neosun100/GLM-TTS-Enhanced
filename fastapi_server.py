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
    voice_id: str = Form(...),
    temperature: float = Form(0.3),
    top_p: float = Form(0.7),
    top_k: int = Form(20),
    skip_whisper: bool = Form(False)
):
    """
    统一TTS接口 - 根据Accept头返回不同格式
    Accept: application/json -> 传统模式
    Accept: text/event-stream -> 流式模式
    """
    accept = request.headers.get('accept', 'application/json')
    
    # 加载语音数据
    json_path = os.path.join(TEMP_DIR, "references", f"{voice_id}.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Voice not found")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        voice_data = json.load(f)
    
    ref_audio_path = os.path.join(TEMP_DIR, "references", f"{voice_id}.wav")
    ref_text = voice_data.get('text', '')
    
    # 流式模式
    if 'text/event-stream' in accept:
        async def generate_stream():
            try:
                # 生成音频
                output_path = await asyncio.to_thread(
                    tts_engine.generate,
                    text=text,
                    ref_audio_path=ref_audio_path,
                    ref_text=ref_text,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    skip_whisper=skip_whisper
                )
                
                # 读取音频文件
                with open(output_path, 'rb') as f:
                    audio_data = f.read()
                
                # 分块推送 (每秒音频 = 48000字节)
                chunk_size = 48000
                total_chunks = (len(audio_data) + chunk_size - 1) // chunk_size
                
                for i in range(total_chunks):
                    chunk = audio_data[i * chunk_size:(i + 1) * chunk_size]
                    import base64
                    chunk_b64 = base64.b64encode(chunk).decode('utf-8')
                    
                    event_data = {
                        "type": "chunk",
                        "index": i,
                        "audio": chunk_b64,
                        "format": "raw_pcm",
                        "sample_rate": 24000,
                        "channels": 1,
                        "sample_width": 2
                    }
                    
                    yield f"data: {json.dumps(event_data)}\n\n"
                    await asyncio.sleep(0.1)
                
                # 完成
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    # 传统模式
    else:
        try:
            output_path = await asyncio.to_thread(
                tts_engine.generate,
                text=text,
                ref_audio_path=ref_audio_path,
                ref_text=ref_text,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                skip_whisper=skip_whisper
            )
            
            filename = os.path.basename(output_path)
            return {
                "success": True,
                "audio_url": f"/voices/{filename}",
                "filename": filename
            }
        except Exception as e:
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
    uvicorn.run(app, host="0.0.0.0", port=port)
