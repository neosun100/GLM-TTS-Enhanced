#!/bin/bash

echo "🧪 GLM-TTS 部署测试"
echo "===================="

PORT=${PORT:-8080}
BASE_URL="http://0.0.0.0:$PORT"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

test_passed=0
test_failed=0

function test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    
    echo -n "测试 $name ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url")
    fi
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((test_passed++))
    else
        echo -e "${RED}✗ 失败 (HTTP $response)${NC}"
        ((test_failed++))
    fi
}

echo ""
echo "1. 基础测试"
echo "----------"
test_endpoint "健康检查" "$BASE_URL/health"
test_endpoint "UI 界面" "$BASE_URL/"
test_endpoint "API 文档" "$BASE_URL/apispec_1.json"

echo ""
echo "2. API 测试"
echo "----------"
test_endpoint "GPU 状态" "$BASE_URL/api/gpu/status"
test_endpoint "GPU 卸载" "$BASE_URL/api/gpu/offload" "POST"

echo ""
echo "3. MCP 测试"
echo "----------"
if [ -f "mcp_server.py" ]; then
    echo -e "${GREEN}✓ MCP 服务器文件存在${NC}"
    ((test_passed++))
else
    echo -e "${RED}✗ MCP 服务器文件不存在${NC}"
    ((test_failed++))
fi

if [ -f "mcp_config.json" ]; then
    echo -e "${GREEN}✓ MCP 配置文件存在${NC}"
    ((test_passed++))
else
    echo -e "${RED}✗ MCP 配置文件不存在${NC}"
    ((test_failed++))
fi

echo ""
echo "===================="
echo "测试结果: ${GREEN}$test_passed 通过${NC}, ${RED}$test_failed 失败${NC}"
echo "===================="

if [ $test_failed -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 部分测试失败${NC}"
    exit 1
fi
