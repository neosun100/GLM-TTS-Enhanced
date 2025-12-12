import os
import sys
import torch
import time
from flask import Flask, request, jsonify, send_file, render_template_string, Response
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

PORT = int(os.getenv('PORT', 8080))
# 使用挂载的临时目录存储上传和生成的音频
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp/glm-tts-voices')
os.makedirs(TEMP_DIR, exist_ok=True)
OUTPUT_DIR = os.path.join(TEMP_DIR, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# TTS Engine
from tts_engine import TTSEngine
tts_engine = TTSEngine(ckpt_dir='./ckpt')
model_loaded = True

# 进度存储
progress_store = {}

@app.route('/')
def index():
    return render_template_string(UI_HTML)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'model_loaded': model_loaded})

@app.route('/api/tts/progress/<task_id>')
def tts_progress(task_id):
    """SSE进度推送"""
    def generate():
        while True:
            if task_id in progress_store:
                progress = progress_store[task_id]
                yield f"data: {jsonify(progress).get_data(as_text=True)}\n\n"
                if progress.get('status') in ['completed', 'error']:
                    del progress_store[task_id]
                    break
            time.sleep(0.5)
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/tts', methods=['POST'])
def tts():
    """
    文本转语音
    ---
    tags:
      - TTS
    consumes:
      - multipart/form-data
    parameters:
      - name: text
        in: formData
        type: string
        required: true
      - name: prompt_audio
        in: formData
        type: file
        required: true
      - name: prompt_text
        in: formData
        type: string
        required: false
    responses:
      200:
        description: 音频文件
    """
    try:
        task_id = str(int(time.time() * 1000))
        progress_store[task_id] = {'status': 'starting', 'step': '初始化', 'elapsed': 0}
        
        print(f"[TTS] Received request, task_id={task_id}")
        start_time = time.time()
        
        text = request.form.get('text')
        prompt_file = request.files.get('prompt_audio')
        prompt_text = request.form.get('prompt_text', '')
        
        # 高级参数
        sampling_strategy = request.form.get('sampling_strategy', 'balanced')
        temperature = float(request.form.get('temperature', 0.8))
        top_p = float(request.form.get('top_p', 0.9))
        skip_whisper = request.form.get('skip_whisper', '0') == '1'
        
        print(f"[TTS] text={text}, prompt_text={prompt_text}, has_file={prompt_file is not None}")
        print(f"[TTS] Advanced: strategy={sampling_strategy}, temp={temperature}, top_p={top_p}, skip_whisper={skip_whisper}")
        
        if not text or not prompt_file:
            print(f"[TTS] Missing required fields")
            return jsonify({'error': 'text and prompt_audio required', 'task_id': task_id}), 400
        
        # Save prompt
        prompt_path = os.path.join(OUTPUT_DIR, f'prompt_{task_id}.wav')
        prompt_file.save(prompt_path)
        print(f"[TTS] Saved prompt to {prompt_path}")
        
        # Generate audio with progress callback
        output_path = os.path.join(OUTPUT_DIR, f'output_{task_id}.wav')
        print(f"[TTS] Starting generation...")
        
        def progress_callback(step, elapsed):
            progress_store[task_id] = {'status': 'processing', 'step': step, 'elapsed': round(elapsed, 1)}
        
        tts_engine.generate(
            text, prompt_path, prompt_text, output_path, 
            progress_callback=progress_callback,
            skip_whisper=skip_whisper,
            temperature=temperature,
            top_p=top_p,
            sampling_strategy=sampling_strategy
        )
        
        elapsed = time.time() - start_time
        progress_store[task_id] = {'status': 'completed', 'step': '完成', 'elapsed': round(elapsed, 1)}
        print(f"[TTS] Generation complete in {elapsed:.1f}s, sending file")
        
        return send_file(output_path, mimetype='audio/wav', as_attachment=True, download_name='generated.wav')
    
    except Exception as e:
        import traceback
        print(f"[TTS] Error: {e}")
        traceback.print_exc()
        if 'task_id' in locals():
            progress_store[task_id] = {'status': 'error', 'step': str(e), 'elapsed': 0}
        return jsonify({'error': str(e)}), 500

@app.route('/api/gpu/status')
def gpu_status():
    """
    GPU 状态
    ---
    tags:
      - GPU
    """
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total', 
                               '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        mem_info = result.stdout.strip().split('\n')[0].split(',')
        return jsonify({
            'loaded': model_loaded,
            'gpu_memory_used': int(mem_info[0]),
            'gpu_memory_total': int(mem_info[1])
        })
    except:
        return jsonify({'loaded': model_loaded, 'gpu_available': False})

@app.route('/api/gpu/offload', methods=['POST'])
def offload_gpu():
    """
    释放 GPU 显存
    ---
    tags:
      - GPU
    """
    global model_loaded
    model_loaded = False
    torch.cuda.empty_cache()
    return jsonify({'status': 'offloaded'})

UI_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GLM-TTS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
               background: #0f0f0f; color: #e0e0e0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .card { background: #1a1a1a; border-radius: 12px; padding: 30px; margin-bottom: 20px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        input[type="text"], textarea { width: 100%; padding: 12px; border: 1px solid #333; 
                                        border-radius: 6px; background: #2a2a2a; color: #e0e0e0; }
        textarea { min-height: 100px; resize: vertical; }
        input[type="file"] { padding: 10px; color: #e0e0e0; }
        button { background: #4CAF50; color: white; padding: 12px 24px; border: none; 
                 border-radius: 6px; cursor: pointer; font-size: 16px; margin-right: 10px; }
        button:hover { background: #45a049; }
        button:disabled { background: #666; cursor: not-allowed; }
        .btn-secondary { background: #666; }
        .btn-secondary:hover { background: #555; }
        .status { padding: 10px; border-radius: 6px; margin-top: 10px; }
        .status.success { background: #1b5e20; }
        .status.error { background: #b71c1c; }
        .gpu-info { display: flex; justify-content: space-between; align-items: center; 
                     padding: 10px; background: #2a2a2a; border-radius: 6px; }
        audio { width: 100%; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎙️ GLM-TTS</h1>
            <p>零样本语音克隆系统</p>
        </div>
        
        <div class="card">
            <div class="gpu-info">
                <span>GPU 状态: <span id="gpu-status">检查中...</span></span>
                <button class="btn-secondary" onclick="offloadGPU()">释放显存</button>
            </div>
        </div>
        
        <div class="card">
            <form id="tts-form" onsubmit="generateTTS(event)">
                <div class="form-group">
                    <label>输入文本</label>
                    <textarea id="text" required>你好，这是一个测试。</textarea>
                </div>
                
                <div class="form-group">
                    <label>参考音频 (3-10秒)</label>
                    <input type="file" id="prompt-audio" accept="audio/*" required>
                </div>
                
                <div class="form-group">
                    <label>参考文本（可选，留空自动识别）</label>
                    <input type="text" id="prompt-text" placeholder="留空将使用Whisper自动识别参考音频内容">
                </div>
                
                <details style="margin-bottom: 20px;">
                    <summary style="cursor: pointer; font-weight: 500; margin-bottom: 10px;">⚙️ 高级参数（可选）</summary>
                    <div style="padding: 10px; background: #2a2a2a; border-radius: 6px;">
                        <div style="background: #3a3a00; padding: 8px; border-radius: 4px; margin-bottom: 15px; font-size: 0.9em;">
                            ⚠️ <strong>实验性功能</strong>：Temperature和Top-p参数目前仅作为UI展示，实际推理暂未生效
                        </div>
                        <div class="form-group">
                            <label>采样策略 (速度 vs 质量) <span style="color: #888; font-size: 0.85em;">[实验性]</span></label>
                            <select id="sampling-strategy" style="width: 100%; padding: 10px; background: #1a1a1a; color: #e0e0e0; border: 1px solid #333; border-radius: 6px;">
                                <option value="balanced">平衡模式 (推荐)</option>
                                <option value="fast">快速模式 (牺牲质量)</option>
                                <option value="quality">高质量模式 (较慢)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Temperature (创造性): <span id="temp-value">0.8</span></label>
                            <input type="range" id="temperature" min="0.1" max="1.5" step="0.1" value="0.8" 
                                   oninput="document.getElementById('temp-value').textContent=this.value"
                                   style="width: 100%;">
                            <small style="color: #888;">较低=更稳定，较高=更多变化</small>
                        </div>
                        <div class="form-group">
                            <label>Top-p (采样范围): <span id="topp-value">0.9</span></label>
                            <input type="range" id="top-p" min="0.5" max="1.0" step="0.05" value="0.9"
                                   oninput="document.getElementById('topp-value').textContent=this.value"
                                   style="width: 100%;">
                            <small style="color: #888;">较低=更确定性，较高=更多样性</small>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="skip-whisper" style="width: auto; margin-right: 8px;">
                                跳过Whisper识别（需手动填写参考文本，可节省2-3秒）
                            </label>
                        </div>
                    </div>
                </details>
                
                <button type="submit" id="submit-btn">生成语音</button>
            </form>
            
            <div id="status"></div>
            <div id="result"></div>
        </div>
    </div>
    
    <script>
        async function updateGPUStatus() {
            try {
                const res = await fetch('/api/gpu/status');
                const data = await res.json();
                let status = data.loaded ? '已加载' : '未加载';
                if (data.gpu_memory_used) {
                    status += ` (${data.gpu_memory_used}MB / ${data.gpu_memory_total}MB)`;
                }
                document.getElementById('gpu-status').textContent = status;
            } catch (e) {
                document.getElementById('gpu-status').textContent = '错误';
            }
        }
        
        async function offloadGPU() {
            await fetch('/api/gpu/offload', { method: 'POST' });
            updateGPUStatus();
        }
        
        async function generateTTS(e) {
            e.preventDefault();
            const btn = document.getElementById('submit-btn');
            const status = document.getElementById('status');
            const result = document.getElementById('result');
            
            btn.disabled = true;
            btn.textContent = '生成中...';
            status.className = 'status';
            status.innerHTML = '<div style="line-height: 1.8;">正在启动...</div>';
            result.innerHTML = '';
            
            const formData = new FormData();
            formData.append('text', document.getElementById('text').value);
            formData.append('prompt_audio', document.getElementById('prompt-audio').files[0]);
            formData.append('prompt_text', document.getElementById('prompt-text').value);
            formData.append('sampling_strategy', document.getElementById('sampling-strategy').value);
            formData.append('temperature', document.getElementById('temperature').value);
            formData.append('top_p', document.getElementById('top-p').value);
            formData.append('skip_whisper', document.getElementById('skip-whisper').checked ? '1' : '0');
            
            const startTime = Date.now();
            let progressLog = [];
            
            // 模拟进度更新（因为后端subprocess无法实时推送）
            const progressInterval = setInterval(() => {
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                status.innerHTML = `<div style="line-height: 1.8;">
                    ${progressLog.join('<br>')}
                    <div style="color: #4CAF50;">⏱️ 已用时: ${elapsed}秒</div>
                </div>`;
            }, 500);
            
            try {
                // 添加初始步骤
                progressLog.push('✓ 上传文件完成');
                
                const res = await fetch('/api/tts', { method: 'POST', body: formData });
                
                clearInterval(progressInterval);
                
                if (res.ok) {
                    const blob = await res.blob();
                    const url = URL.createObjectURL(blob);
                    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                    result.innerHTML = `<audio controls src="${url}"></audio>`;
                    status.className = 'status success';
                    status.innerHTML = `<div style="line-height: 1.8;">
                        ${progressLog.join('<br>')}
                        <div style="color: #4CAF50; font-weight: bold;">✓ 生成成功！总用时: ${elapsed}秒</div>
                    </div>`;
                } else {
                    const contentType = res.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        const err = await res.json();
                        throw new Error(err.error || 'Unknown error');
                    } else {
                        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
                    }
                }
            } catch (err) {
                clearInterval(progressInterval);
                status.className = 'status error';
                status.textContent = '错误: ' + err.message;
            } finally {
                btn.disabled = false;
                btn.textContent = '生成语音';
                updateGPUStatus();
            }
        }
        
        setInterval(updateGPUStatus, 5000);
        updateGPUStatus();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print(f"🚀 Starting GLM-TTS Server on port {PORT}")
    print(f"📱 UI: http://0.0.0.0:{PORT}")
    print(f"📚 API Docs: http://0.0.0.0:{PORT}/docs")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
