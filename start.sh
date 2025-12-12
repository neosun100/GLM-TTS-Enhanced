#!/bin/bash

set -e

echo "🚀 GLM-TTS Docker 启动脚本"
echo "=========================="

# 检查 nvidia-docker
if ! docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
    echo "❌ nvidia-docker 环境检查失败"
    exit 1
fi
echo "✅ nvidia-docker 环境正常"

# 自动选择最空闲的 GPU
GPU_ID=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | \
         sort -t',' -k2 -n | head -1 | cut -d',' -f1)
echo "🎯 自动选择 GPU: $GPU_ID"

# 检查端口占用
PORT=${PORT:-8080}
if ss -tuln | grep -q ":$PORT "; then
    echo "❌ 端口 $PORT 已被占用，请修改 .env 文件"
    exit 1
fi
echo "✅ 端口 $PORT 可用"

# 创建 .env 文件
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 已创建 .env 文件"
fi

# 设置环境变量
export NVIDIA_VISIBLE_DEVICES=$GPU_ID
export PORT=$PORT

# 启动服务
echo "🔧 启动 Docker Compose..."
docker-compose up -d --build

echo ""
echo "✅ 服务启动成功！"
echo "=========================="
echo "📱 UI 界面: http://0.0.0.0:$PORT"
echo "📚 API 文档: http://0.0.0.0:$PORT/docs"
echo "🔧 MCP 端口: $PORT"
echo "🎮 GPU: $GPU_ID"
echo "=========================="
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
