"""
Voice Cache API Endpoints
语音缓存相关的API端点
"""
from flask import request, jsonify, send_file
import os
import time

def register_voice_api(app, tts_engine, progress_store, OUTPUT_DIR):
    """注册语音缓存相关的API端点"""
    
    @app.route('/api/voices', methods=['GET'])
    def list_voices():
        """
        列出所有缓存的语音
        ---
        tags:
          - Voice Cache
        responses:
          200:
            description: 语音列表
            schema:
              type: object
              properties:
                voices:
                  type: array
                  items:
                    type: object
                stats:
                  type: object
        """
        try:
            voices = tts_engine.list_cached_voices()
            stats = tts_engine.get_cache_stats()
            return jsonify({
                'voices': voices,
                'stats': stats
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voices', methods=['POST'])
    def create_voice():
        """
        创建语音缓存
        ---
        tags:
          - Voice Cache
        consumes:
          - multipart/form-data
        parameters:
          - name: audio
            in: formData
            type: file
            required: true
            description: 参考音频文件
          - name: prompt_text
            in: formData
            type: string
            required: false
            description: 参考文本（可选，留空自动识别）
          - name: skip_whisper
            in: formData
            type: boolean
            required: false
            description: 是否跳过Whisper识别
        responses:
          200:
            description: 创建成功
            schema:
              type: object
              properties:
                voice_id:
                  type: string
                metadata:
                  type: object
        """
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            audio_file = request.files['audio']
            prompt_text = request.form.get('prompt_text', '')
            skip_whisper = request.form.get('skip_whisper', 'false').lower() == 'true'
            
            # 保存上传的音频
            timestamp = int(time.time() * 1000)
            audio_path = os.path.join(OUTPUT_DIR, f'voice_{timestamp}.wav')
            audio_file.save(audio_path)
            
            # 创建缓存
            voice_id, metadata = tts_engine.cache_voice_from_audio(
                audio_path=audio_path,
                prompt_text=prompt_text,
                skip_whisper=skip_whisper
            )
            
            return jsonify({
                'voice_id': voice_id,
                'metadata': metadata,
                'message': 'Voice cached successfully'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voices/<voice_id>', methods=['GET'])
    def get_voice(voice_id):
        """
        获取语音信息
        ---
        tags:
          - Voice Cache
        parameters:
          - name: voice_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: 语音信息
          404:
            description: 语音不存在
        """
        try:
            cached_voice = tts_engine.voice_cache.load_voice(voice_id)
            if not cached_voice:
                return jsonify({'error': 'Voice not found'}), 404
            
            return jsonify({
                'voice_id': voice_id,
                'metadata': cached_voice['metadata']
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voices/<voice_id>', methods=['DELETE'])
    def delete_voice(voice_id):
        """
        删除语音缓存
        ---
        tags:
          - Voice Cache
        parameters:
          - name: voice_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: 删除成功
          404:
            description: 语音不存在
        """
        try:
            success = tts_engine.delete_cached_voice(voice_id)
            if not success:
                return jsonify({'error': 'Voice not found'}), 404
            
            return jsonify({'message': 'Voice deleted successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voices/<voice_id>/audio', methods=['GET'])
    def get_voice_audio(voice_id):
        """
        获取语音的参考音频文件
        ---
        tags:
          - Voice Cache
        parameters:
          - name: voice_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: 音频文件
          404:
            description: 语音不存在
        """
        try:
            audio_path = tts_engine.voice_cache.get_audio_path(voice_id)
            if not audio_path or not os.path.exists(audio_path):
                return jsonify({'error': 'Audio file not found'}), 404
            
            return send_file(audio_path, mimetype='audio/wav')
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/tts/with_voice', methods=['POST'])
    def tts_with_voice():
        """
        使用缓存的语音ID生成TTS（快速模式）
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
            description: 要合成的文本
          - name: voice_id
            in: formData
            type: string
            required: true
            description: 语音ID
          - name: temperature
            in: formData
            type: number
            required: false
            description: Temperature参数 (0.1-1.5)
          - name: top_p
            in: formData
            type: number
            required: false
            description: Top-p参数 (0.5-1.0)
          - name: sampling_strategy
            in: formData
            type: string
            required: false
            description: 采样策略 (fast/balanced/quality)
        responses:
          200:
            description: 音频文件
        """
        try:
            task_id = str(int(time.time() * 1000))
            progress_store[task_id] = {'status': 'starting', 'step': '初始化', 'elapsed': 0}
            
            text = request.form.get('text')
            voice_id = request.form.get('voice_id')
            temperature = float(request.form.get('temperature', 0.8))
            top_p = float(request.form.get('top_p', 0.9))
            sampling_strategy = request.form.get('sampling_strategy', 'balanced')
            
            if not text or not voice_id:
                return jsonify({'error': 'Missing required parameters'}), 400
            
            # 检查voice_id是否存在
            if not tts_engine.voice_cache.exists(voice_id):
                return jsonify({'error': f'Voice ID not found: {voice_id}'}), 404
            
            print(f"[TTS] Using voice_id={voice_id}, task_id={task_id}")
            
            # 生成输出路径
            output_filename = f'output_{task_id}.wav'
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            # 进度回调
            def progress_callback(step, elapsed):
                progress_store[task_id] = {
                    'status': 'processing',
                    'step': step,
                    'elapsed': round(elapsed, 1)
                }
            
            # 使用voice_id生成
            result_path, used_voice_id = tts_engine.generate_with_voice_id(
                text=text,
                voice_id=voice_id,
                output_path=output_path,
                progress_callback=progress_callback,
                temperature=temperature,
                top_p=top_p,
                sampling_strategy=sampling_strategy
            )
            
            progress_store[task_id] = {'status': 'completed', 'step': '完成', 'elapsed': 0}
            
            return send_file(result_path, mimetype='audio/wav', as_attachment=True,
                           download_name=output_filename)
            
        except Exception as e:
            print(f"[TTS] Error: {e}")
            import traceback
            traceback.print_exc()
            progress_store[task_id] = {'status': 'error', 'step': str(e), 'elapsed': 0}
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cache/stats', methods=['GET'])
    def cache_stats():
        """
        获取缓存统计信息
        ---
        tags:
          - Voice Cache
        responses:
          200:
            description: 缓存统计
        """
        try:
            stats = tts_engine.get_cache_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("[API] Voice cache endpoints registered")
