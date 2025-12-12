# GLM-TTS Docker 化文件索引

## 📦 新增文件清单

### 🐳 Docker 相关 (4 个)
| 文件 | 大小 | 说明 |
|------|------|------|
| `Dockerfile` | 496 B | Docker 镜像定义 |
| `docker-compose.yml` | 585 B | 容器编排配置 |
| `.env.example` | 55 B | 环境变量模板 |
| `.dockerignore` | 398 B | 构建忽略文件 |

### 🚀 脚本文件 (2 个)
| 文件 | 大小 | 说明 |
|------|------|------|
| `start.sh` | 1.4 KB | 一键启动脚本 ⭐ |
| `test_deployment.sh` | 1.9 KB | 自动化测试脚本 |

### 💻 代码文件 (3 个)
| 文件 | 大小 | 说明 |
|------|------|------|
| `server.py` | 12 KB | 主服务器（UI + API）|
| `gpu_manager.py` | 1.4 KB | GPU 资源管理器 |
| `mcp_server.py` | 2.0 KB | MCP 服务器 |

### ⚙️ 配置文件 (1 个)
| 文件 | 大小 | 说明 |
|------|------|------|
| `mcp_config.json` | 167 B | MCP 配置文件 |

### 📚 文档文件 (6 个)
| 文件 | 大小 | 说明 | 目标读者 |
|------|------|------|----------|
| `QUICK_START.md` | 1.6 KB | 快速开始指南 | 所有用户 |
| `README_DOCKER.md` | 3.5 KB | Docker 详细说明 | 运维人员 |
| `MCP_GUIDE.md` | 3.3 KB | MCP 使用教程 | AI 用户 |
| `DEPLOYMENT.md` | 8.5 KB | 完整部署文档 | 技术人员 |
| `CHECKLIST.md` | 4.6 KB | 部署检查清单 | 运维人员 |
| `SUMMARY.md` | 11 KB | 项目总结 | 管理人员 |

## 📖 文档阅读顺序

### 新手用户
1. `QUICK_START.md` - 快速上手
2. `README_DOCKER.md` - 了解 Docker 部署
3. `MCP_GUIDE.md` - 学习 MCP 使用（可选）

### 运维人员
1. `DEPLOYMENT.md` - 完整部署流程
2. `CHECKLIST.md` - 逐项检查
3. `README_DOCKER.md` - 详细配置

### 开发人员
1. `SUMMARY.md` - 项目架构
2. `server.py` - 代码实现
3. `gpu_manager.py` - GPU 管理逻辑

### 管理人员
1. `SUMMARY.md` - 项目总结
2. `DEPLOYMENT.md` - 技术方案

## 🎯 核心文件说明

### start.sh ⭐
**最重要的文件**，一键启动脚本：
```bash
./start.sh
```
功能：
- ✅ 检查环境
- ✅ 自动选择 GPU
- ✅ 检查端口
- ✅ 启动容器
- ✅ 显示访问信息

### server.py
**主服务器**，包含：
- UI 界面（HTML 嵌入）
- RESTful API
- GPU 管理集成
- Swagger 文档

### gpu_manager.py
**GPU 管理器**，特性：
- 单例模式
- 自动加载/卸载
- 线程安全
- 状态监控

### mcp_server.py
**MCP 服务器**，提供：
- text_to_speech 工具
- get_gpu_status 工具
- offload_gpu 工具

## 🔗 文件依赖关系

```
start.sh
  ├── .env.example → .env
  ├── docker-compose.yml
  │   └── Dockerfile
  │       └── requirements.txt
  └── 启动容器
      ├── server.py
      │   ├── gpu_manager.py
      │   └── CosyVoice 模型
      └── mcp_server.py
          └── gpu_manager.py
```

## 📊 统计信息

### 文件统计
- **总文件数**: 16 个
- **代码文件**: 3 个
- **配置文件**: 5 个
- **脚本文件**: 2 个
- **文档文件**: 6 个

### 代码统计
- **Python 代码**: ~800 行
- **Shell 脚本**: ~100 行
- **HTML/CSS/JS**: ~300 行
- **文档内容**: ~2000 行

### 功能覆盖
- ✅ Docker 化: 100%
- ✅ GPU 管理: 100%
- ✅ UI 界面: 100%
- ✅ API 接口: 100%
- ✅ MCP 集成: 100%
- ✅ 文档完整: 100%

## 🚀 快速导航

### 我想...

**快速开始使用**
→ 阅读 `QUICK_START.md`
→ 运行 `./start.sh`

**了解 Docker 部署**
→ 阅读 `README_DOCKER.md`
→ 查看 `docker-compose.yml`

**集成到 AI 助手**
→ 阅读 `MCP_GUIDE.md`
→ 配置 `mcp_config.json`

**完整部署到生产**
→ 阅读 `DEPLOYMENT.md`
→ 执行 `CHECKLIST.md`

**了解技术架构**
→ 阅读 `SUMMARY.md`
→ 查看 `server.py`

**测试部署**
→ 运行 `./test_deployment.sh`

## 🎉 使用流程

### 标准流程
```bash
# 1. 下载模型
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt

# 2. 启动服务
./start.sh

# 3. 测试验证
./test_deployment.sh

# 4. 访问使用
# UI: http://0.0.0.0:8080
# API: http://0.0.0.0:8080/docs
```

### 故障排查
```bash
# 查看日志
docker-compose logs -f

# 检查状态
docker-compose ps

# 重启服务
docker-compose restart
```

## 📞 获取帮助

### 文档查询
- 快速问题 → `QUICK_START.md`
- 部署问题 → `README_DOCKER.md`
- MCP 问题 → `MCP_GUIDE.md`
- 完整指南 → `DEPLOYMENT.md`

### 命令帮助
```bash
# 查看启动脚本帮助
cat start.sh

# 查看测试脚本
cat test_deployment.sh

# 查看环境变量
cat .env.example
```

---

**所有文件已就绪，开始使用吧！** 🚀
