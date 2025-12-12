"""
FastAPI流式服务 - 更好的SSE支持
"""
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import base64
import wave
import tempfile
import os
import sys

# 导入TTS引擎
sys.path.insert(0, '/app')
from tts_engine import TTSEngine

app = FastAPI(title="GLM-TTS Streaming API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化TTS引擎
tts_engine = TTSEngine(ckpt_dir='/app/ckpt', enable_memory_cache=True)

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": True}

@app.post("/api/tts/stream")
async def tts_stream(
    text: str = Form(...),
    voice_id: str = Form(...)
):
    """流式TTS生成"""
    
    async def generate():
        try:
            # 生成完整音频
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                output_path = tmp.name
            
            try:
                # 使用TTS引擎生成
                result_path, _ = tts_engine.generate_with_voice_id(
                    text=text,
                    voice_id=voice_id,
                    output_path=output_path
                )
                
                # 读取并分块发送
                with wave.open(result_path, 'rb') as wf:
                    chunk_size = wf.getframerate() * 1  # 1秒
                    chunk_index = 0
                    
                    while True:
                        frames = wf.readframes(chunk_size)
                        if not frames:
                            break
                        
                        # 构建SSE消息
                        audio_b64 = base64.b64encode(frames).decode()
                        chunk_data = {
                            'type': 'chunk',
                            'index': chunk_index,
                            'audio': audio_b64,
                            'format': 'raw_pcm',
                            'sample_rate': wf.getframerate(),
                            'channels': wf.getnchannels(),
                            'sample_width': wf.getsampwidth()
                        }
                        
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                        chunk_index += 1
                
                # 发送完成信号
                yield f"data: {json.dumps({'type': 'done', 'total_chunks': chunk_index})}\n\n"
                
            finally:
                if os.path.exists(output_path):
                    os.remove(output_path)
                    
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
