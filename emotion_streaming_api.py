"""
情感控制和流式推理API - GLM-TTS v1.2.0
"""
from flask import Blueprint, request, jsonify, Response, stream_with_context
from emotion_control import EmotionController
from streaming_engine import StreamingEngine

emotion_streaming_bp = Blueprint('emotion_streaming', __name__)

# 全局实例
emotion_controller = EmotionController()
streaming_engine = StreamingEngine()

@emotion_streaming_bp.route('/api/emotions', methods=['GET'])
def list_emotions():
    """列出所有支持的情感类型"""
    return jsonify({
        'success': True,
        'emotions': EmotionController.list_emotions()
    })

@emotion_streaming_bp.route('/api/voices/<voice_id>/emotion', methods=['POST'])
def set_voice_emotion(voice_id):
    """为语音ID设置情感"""
    data = request.get_json()
    emotion_type = data.get('emotion', 'neutral')
    intensity = data.get('intensity')
    
    try:
        result = emotion_controller.set_emotion(emotion_type, intensity)
        
        # 保存到voice cache metadata
        from server import tts_engine
        voice_info = tts_engine.voice_cache.get_voice(voice_id)
        if voice_info:
            metadata = voice_info.get('metadata', {})
            metadata['emotion'] = result
            # 更新缓存（简化版，实际需要完整实现）
            
        return jsonify({
            'success': True,
            'voice_id': voice_id,
            'emotion': result
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@emotion_streaming_bp.route('/api/tts/stream', methods=['POST'])
def tts_stream():
    """流式TTS生成"""
    text = request.form.get('text')
    voice_id = request.form.get('voice_id')
    emotion = request.form.get('emotion', 'neutral')
    intensity = float(request.form.get('emotion_intensity', 0.0))
    
    if not text or not voice_id:
        return jsonify({'error': 'text和voice_id必填'}), 400
    
    # 设置情感
    emotion_controller.set_emotion(emotion, intensity)
    emotion_params = emotion_controller.get_emotion_params()
    
    # 流式生成
    from server import tts_engine
    
    def generate():
        for chunk in streaming_engine.generate_stream(
            tts_engine, text, voice_id, emotion_params
        ):
            yield chunk
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@emotion_streaming_bp.route('/api/tts/stream/status', methods=['GET'])
def stream_status():
    """获取流式生成状态"""
    return jsonify({
        'is_generating': streaming_engine.is_generating
    })

@emotion_streaming_bp.route('/api/tts/stream/stop', methods=['POST'])
def stream_stop():
    """停止流式生成"""
    streaming_engine.stop()
    return jsonify({'success': True})
