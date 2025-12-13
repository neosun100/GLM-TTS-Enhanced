#!/bin/bash

# GLM-TTS Performance Test Script
# 测试不同文本长度的生成速度

API_URL="http://localhost:8080"
REFERENCE_AUDIO="/tmp/glm-tts-voices/references/20251212_121515.wav"
PROMPT_TEXT="这是一段测试语音"
OUTPUT_DIR="/tmp/glm-tts-test-results"

# 创建输出目录
mkdir -p $OUTPUT_DIR

# 测试文本（不同长度）
declare -a TEST_TEXTS=(
    "今天天气真不错。"  # 短文本：8字
    "人工智能正在改变我们的生活方式，语音合成技术让机器拥有了人类的声音。"  # 中文本：30字
    "随着科技的发展，人工智能已经渗透到我们生活的方方面面。从智能手机到自动驾驶汽车，从语音助手到智能家居，AI技术正在以前所未有的速度改变着世界。"  # 长文本：60字
    "在数字化时代，人工智能技术的应用越来越广泛。机器学习、深度学习、自然语言处理等技术的突破，使得计算机能够理解和生成人类语言，识别图像和声音，甚至进行复杂的决策。这些技术不仅提高了工作效率，也为人们的生活带来了便利。"  # 超长文本：100字
    "语音合成技术是人工智能领域的重要分支之一。通过深度学习模型，我们可以让计算机学习人类的发音方式、语调变化和情感表达。现代的语音合成系统不仅能够生成自然流畅的语音，还能够模仿特定人物的声音特征，实现声音克隆。这项技术在有声读物、语音助手、影视配音等领域有着广泛的应用前景。随着技术的不断进步，未来的语音合成将更加智能化和个性化。"  # 极长文本：150字
)

# 文本长度标签
declare -a TEXT_LABELS=(
    "短文本(8字)"
    "中文本(30字)"
    "长文本(60字)"
    "超长文本(100字)"
    "极长文本(150字)"
)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         GLM-TTS v2.3.1 性能测试                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "API地址: $API_URL"
echo "参考音频: $REFERENCE_AUDIO"
echo ""

# 测试标准TTS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "【测试1】标准TTS性能测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for i in "${!TEST_TEXTS[@]}"; do
    text="${TEST_TEXTS[$i]}"
    label="${TEXT_LABELS[$i]}"
    
    echo "测试 $((i+1))/5: $label"
    echo "文本: ${text:0:30}..."
    
    # 执行测试并记录时间
    start_time=$(date +%s.%N)
    
    curl -s -X POST $API_URL/api/tts \
      -F "text=$text" \
      -F "prompt_audio=@$REFERENCE_AUDIO" \
      -F "prompt_text=$PROMPT_TEXT" \
      -F "skip_whisper=true" \
      -o "$OUTPUT_DIR/standard_test_$i.wav" 2>/dev/null
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    # 获取文件大小
    file_size=$(ls -lh "$OUTPUT_DIR/standard_test_$i.wav" | awk '{print $5}')
    
    echo "✅ 完成 - 耗时: ${duration}秒 - 文件大小: $file_size"
    echo ""
    
    # 保存结果
    echo "$label,$duration,$file_size" >> "$OUTPUT_DIR/standard_results.csv"
    
    # 短暂延迟避免过载
    sleep 1
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "【测试2】流式TTS性能测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查是否有流式端点
if curl -s "$API_URL/openapi.json" | grep -q "/api/tts/stream"; then
    for i in "${!TEST_TEXTS[@]}"; do
        text="${TEST_TEXTS[$i]}"
        label="${TEXT_LABELS[$i]}"
        
        echo "测试 $((i+1))/5: $label"
        echo "文本: ${text:0:30}..."
        
        # 执行测试并记录时间（不保存SSE输出）
        start_time=$(date +%s.%N)
        
        curl -s -X POST $API_URL/api/tts/stream \
          -F "text=$text" \
          -F "prompt_audio=@$REFERENCE_AUDIO" \
          -F "prompt_text=$PROMPT_TEXT" \
          -F "skip_whisper=true" \
          > /dev/null 2>&1
        
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        
        echo "✅ 完成 - 耗时: ${duration}秒"
        echo ""
        
        # 保存结果
        echo "$label,$duration" >> "$OUTPUT_DIR/stream_results.csv"
        
        # 短暂延迟
        sleep 1
    done
else
    echo "⚠️  流式TTS端点不可用，跳过测试"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试完成！结果已保存到: $OUTPUT_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
