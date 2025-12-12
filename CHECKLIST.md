# GLM-TTS 部署检查清单 ✅

## 📋 部署前检查

### 环境要求
- [ ] Linux 系统（已确认：Ubuntu/Debian）
- [ ] Docker 已安装
- [ ] nvidia-docker 已配置
- [ ] GPU 可用（至少一张）
- [ ] Python 3.10-3.12

### 文件完整性
- [x] Dockerfile
- [x] docker-compose.yml
- [x] .env.example
- [x] .dockerignore
- [x] start.sh
- [x] test_deployment.sh
- [x] server.py
- [x] gpu_manager.py
- [x] mcp_server.py
- [x] mcp_config.json

### 模型文件
- [ ] ckpt/ 目录存在
- [ ] 模型权重已下载
- [ ] 前端模型文件完整

## 🚀 部署步骤

### 1. 准备阶段
```bash
# 检查 GPU
nvidia-smi

# 检查 Docker
docker --version
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# 检查端口
ss -tuln | grep 8080
```

### 2. 下载模型
```bash
# 方式一：HuggingFace
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt

# 方式二：ModelScope
modelscope download --model ZhipuAI/GLM-TTS --local_dir ckpt
```

### 3. 配置环境
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置（可选）
nano .env
```

### 4. 启动服务
```bash
# 一键启动
./start.sh

# 或手动启动
docker-compose up -d --build
```

### 5. 验证部署
```bash
# 运行测试
./test_deployment.sh

# 检查日志
docker-compose logs -f
```

## 🧪 功能测试

### UI 界面测试
- [ ] 访问 http://0.0.0.0:8080
- [ ] 页面正常加载
- [ ] 语言切换正常
- [ ] GPU 状态显示
- [ ] 文件上传功能
- [ ] 音频生成功能
- [ ] 音频播放功能
- [ ] 释放显存按钮

### API 测试
- [ ] Swagger 文档可访问 (/docs)
- [ ] 健康检查 (/health)
- [ ] GPU 状态查询 (/api/gpu/status)
- [ ] GPU 卸载 (/api/gpu/offload)
- [ ] TTS 接口 (/api/tts)

### MCP 测试
- [ ] mcp_server.py 可运行
- [ ] mcp_config.json 配置正确
- [ ] 工具函数可调用
- [ ] GPU 管理器共享正常

## 📊 性能测试

### GPU 管理
- [ ] 首次调用自动加载模型
- [ ] 空闲超时自动卸载
- [ ] 手动卸载功能正常
- [ ] 多次调用不重复加载

### 并发测试
```bash
# 测试并发请求
for i in {1..5}; do
  curl -X POST http://0.0.0.0:8080/api/tts \
    -F "text=测试$i" \
    -F "prompt_audio=@examples/prompt/zh.wav" \
    -o "output_$i.wav" &
done
wait
```

### 内存监控
```bash
# 监控 GPU 显存
watch -n 1 nvidia-smi

# 监控容器资源
docker stats glm-tts
```

## 🔒 安全检查

### 网络安全
- [ ] 端口绑定到 0.0.0.0（按需求）
- [ ] 防火墙规则配置
- [ ] 考虑添加认证机制

### 数据安全
- [ ] 输出目录权限正确
- [ ] 临时文件自动清理
- [ ] 敏感信息不在日志中

## 📝 文档检查

### 用户文档
- [x] README.md（项目主文档）
- [x] README_DOCKER.md（Docker 指南）
- [x] MCP_GUIDE.md（MCP 使用）
- [x] DEPLOYMENT.md（部署总览）
- [x] QUICK_START.md（快速开始）
- [x] CHECKLIST.md（本清单）

### 代码文档
- [x] 函数注释完整
- [x] 类型注解完整
- [x] API 文档（Swagger）
- [x] MCP 工具描述

## 🎯 生产环境额外检查

### 高可用
- [ ] 配置容器重启策略
- [ ] 设置健康检查
- [ ] 配置日志轮转
- [ ] 监控告警设置

### 性能优化
- [ ] GPU 超时参数调优
- [ ] 并发限制设置
- [ ] 缓存策略配置
- [ ] 负载均衡（如需要）

### 备份恢复
- [ ] 模型文件备份
- [ ] 配置文件备份
- [ ] 数据恢复测试

## ✅ 最终验证

### 基础功能
```bash
# 1. UI 访问
curl -I http://0.0.0.0:8080

# 2. API 健康检查
curl http://0.0.0.0:8080/health

# 3. GPU 状态
curl http://0.0.0.0:8080/api/gpu/status

# 4. 完整测试
./test_deployment.sh
```

### 端到端测试
```bash
# 使用示例音频生成
curl -X POST http://0.0.0.0:8080/api/tts \
  -F "text=这是一个完整的端到端测试" \
  -F "prompt_audio=@examples/prompt/zh.wav" \
  -o test_output.wav

# 验证输出
file test_output.wav
```

## 📞 问题报告

如遇问题，收集以下信息：

```bash
# 系统信息
uname -a
docker --version
nvidia-smi

# 容器状态
docker-compose ps
docker-compose logs --tail=100

# GPU 状态
nvidia-smi
curl http://0.0.0.0:8080/api/gpu/status

# 端口占用
ss -tuln | grep 8080
```

## 🎉 部署完成

所有检查项通过后，部署完成！

**访问地址**：
- UI: http://0.0.0.0:8080
- API: http://0.0.0.0:8080/docs
- MCP: 见 MCP_GUIDE.md

**常用命令**：
```bash
docker-compose logs -f    # 查看日志
docker-compose restart    # 重启服务
docker-compose down       # 停止服务
./test_deployment.sh      # 运行测试
```

---

**祝使用愉快！** 🎙️
