#!/bin/bash
echo "=========================================="
echo "GLM-TTS v1.2.0 最终验证测试"
echo "=========================================="

echo -e "\n1. 检查Docker镜像"
docker images | grep "neosun/glm-tts" | grep "v1.2.0"

echo -e "\n2. 检查容器状态"
docker ps | grep glm-tts

echo -e "\n3. 测试健康检查"
curl -s http://localhost:8080/health | jq .

echo -e "\n4. 测试情感API"
curl -s http://localhost:8080/api/emotions | jq '.emotions | keys'

echo -e "\n5. 测试设置情感"
curl -s -X POST http://localhost:8080/api/voices/e2d8cdc3/emotion \
  -H "Content-Type: application/json" \
  -d '{"emotion": "happy", "intensity": 0.8}' | jq .

echo -e "\n6. 检查voice cache"
curl -s http://localhost:8080/api/cache/stats | jq .

echo -e "\n=========================================="
echo "✓ v1.2.0 验证完成"
echo "=========================================="
