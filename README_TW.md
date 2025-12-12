[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# GLM-TTS 增強版：生產級 TTS 服務

[![Docker Hub](https://img.shields.io/docker/v/neosun/glm-tts?label=Docker%20Hub)](https://hub.docker.com/r/neosun/glm-tts)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://www.python.org/)

GLM-TTS 的增強版本，提供生產級功能：Web UI、REST API、Whisper 自動轉錄和 Docker 部署。

![GLM-TTS Enhanced UI](https://img.aws.xin/uPic/YD5e2C.png)

## ✨ 增強功能

### 🎯 核心增強
- **🌐 現代化 Web 介面**：響應式介面，即時進度追蹤
- **🔌 REST API**：完整的 API，Swagger 文件位於 `/apidocs`
- **🎤 Whisper 整合**：參考文字為空時自動音訊轉錄
- **📊 即時進度**：基於 SSE 的串流傳輸，顯示耗時
- **🐳 一體化 Docker**：23.6GB 映像包含所有模型和依賴
- **⚡ GPU 優化**：cuDNN 9 支援 ONNX Runtime GPU 加速
- **💾 持久化儲存**：掛載主機目錄進行檔案管理
- **🔧 進階控制**：Temperature、Top-p 和採樣策略參數
- **🤖 MCP 伺服器**：Model Context Protocol 伺服器用於 AI 代理整合

### 🆕 新增特性
- Whisper 自動轉錄（參考文字留空即可）
- 即時生成進度與計時
- 實驗性進階參數
- 檔案儲存在主機 `/tmp/glm-tts-voices`
- 完整的 ONNX Runtime GPU 加速（cuDNN 9）
- MCP 伺服器無縫整合 AI 代理

## 🚀 快速開始（推薦）

### 使用 Docker（一體化映像）

```bash
# 拉取最新 v2.3.1 映像
docker pull neosun/glm-tts:all-in-one-fastapi-v2.3.1

# 建立臨時目錄
mkdir -p /tmp/glm-tts-voices
chmod 777 /tmp/glm-tts-voices

# 使用 GPU 0 執行（根據需要更改裝置 ID）
docker run -d \
  --name glm-tts \
  --runtime=nvidia \
  -e NVIDIA_VISIBLE_DEVICES=0 \
  -e PORT=8080 \
  -e TEMP_DIR=/tmp/glm-tts-voices \
  -p 8080:8080 \
  -v /tmp/glm-tts-voices:/tmp/glm-tts-voices \
  --restart unless-stopped \
  neosun/glm-tts:all-in-one-fastapi-v2.3.1
```

**存取 Web 介面**：`http://localhost:8080`

### 使用 Docker Compose

```yaml
version: '3.8'

services:
  glm-tts:
    image: neosun/glm-tts:all-in-one
    container_name: glm-tts
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0
      - PORT=8080
      - TEMP_DIR=/tmp/glm-tts-voices
    ports:
      - "8080:8080"
    volumes:
      - /tmp/glm-tts-voices:/tmp/glm-tts-voices
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
```

啟動服務：
```bash
docker-compose up -d
```

## 📖 使用方法

### Web 介面

1. 在瀏覽器中開啟 `http://localhost:8080`
2. 上傳參考音訊檔案（3-10 秒，WAV 格式）
3. 輸入要合成的文字
4. **可選**：參考文字留空，透過 Whisper 自動轉錄
5. **可選**：展開「進階參數」進行微調
6. 點擊「生成語音」並觀察即時進度
7. 下載生成的音訊

### REST API

**生成語音：**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=你好，這是一個測試。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=參考音訊文字" \
  -F "temperature=0.8" \
  -F "top_p=0.9" \
  -F "sampling_strategy=balanced"
```

**API 文件**：存取 `http://localhost:8080/apidocs` 檢視互動式 Swagger 文件。

**健康檢查：**
```bash
curl http://localhost:8080/health
```

### MCP 伺服器整合

專案包含 MCP（Model Context Protocol）伺服器用於 AI 代理整合：

```bash
# 啟動 MCP 伺服器
python mcp_server.py

# 在 AI 代理中設定（例如 Claude Desktop）
# 詳見 MCP_GUIDE.md
```

### 進階參數

- **Temperature** (0.1-1.5)：控制隨機性（越高越多樣化）
- **Top-p** (0.5-1.0)：核採樣閾值
- **採樣策略**：
  - `fast`：快速生成，品質較低
  - `balanced`：預設，品質/速度平衡
  - `quality`：最佳品質，生成較慢
- **跳過 Whisper**：停用自動轉錄以加快處理

## 🏗️ 架構

```
┌─────────────────┐
│   Web UI        │
│  (HTML/JS)      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Flask 伺服器   │
│  (server.py)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  TTS 引擎       │
│ (tts_engine.py) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Whisper│  │GLM-TTS│
│ 模型  │  │ 模型  │
└───────┘  └───────┘
```

### 增強元件

| 元件 | 說明 |
|------|------|
| `server.py` | Flask REST API 與 SSE 進度流 |
| `tts_engine.py` | TTS 推理引擎與 Whisper 整合 |
| `mcp_server.py` | MCP 伺服器用於 AI 代理整合 |
| `Dockerfile` | 多階段建置與 cuDNN 9 |
| `docker-compose.yml` | 生產部署設定 |

## 🔧 設定

### 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `PORT` | 8080 | 伺服器埠 |
| `TEMP_DIR` | `/tmp/glm-tts-voices` | 臨時檔案儲存 |
| `GPU_IDLE_TIMEOUT` | 60 | GPU 閒置逾時（秒） |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU 裝置 ID |

### GPU 選擇

使用特定 GPU（例如 GPU 2）：

```bash
docker run -e NVIDIA_VISIBLE_DEVICES=2 ...
```

或在 `docker-compose.yml` 中：
```yaml
environment:
  - NVIDIA_VISIBLE_DEVICES=2
deploy:
  resources:
    reservations:
      devices:
        - device_ids: ['2']
```

## 📊 效能

- **模型大小**：23.6GB（v2.3.1一體化映像）
- **顯存使用**：推理時約 12GB
- **生成速度**：10秒音訊需2-3秒（比v2.0.0快20-30倍）
- **Whisper 開銷**：自動轉錄增加 2-3 秒
- **啟動時間**：約90秒（一次性模型載入）
- **模型快取**：所有模型常駐GPU記憶體，實現即時推理

## 🛠️ 故障排除

### 常見問題

**CUDA 記憶體不足**
- 使用更大顯存的 GPU（推薦 16GB+）
- 關閉其他 GPU 應用程式

**cuDNN 版本不符**
- 使用提供的 Docker 映像（已包含 cuDNN 9）
- 檢查：`ldconfig -p | grep cudnn`

**生成緩慢**
- 驗證 GPU 使用：`nvidia-smi`
- 檢查 NVIDIA_VISIBLE_DEVICES 是否符合您的 GPU

**Whisper 失敗**
- 確保音訊清晰且格式受支援
- 使用 `skip_whisper=true` 繞過

## 📦 從原始碼建置

```bash
# 建置 Docker 映像
docker build -t glm-tts:custom .

# 推送到儲存庫
docker tag glm-tts:custom your-registry/glm-tts:latest
docker push your-registry/glm-tts:latest
```

## 🤝 貢獻

歡迎貢獻！請：

1. Fork 儲存庫
2. 建立功能分支
3. 提交更改
4. 推送到分支
5. 開啟 Pull Request

## 📝 更新日誌

### v2.3.1 (2025-12-13)
- ⚡ **20-30倍效能提升**：推理時間從60秒降至2-3秒
- 🏗️ 架構重構：TTSEngine直接載入模型，消除subprocess開銷
- 💾 模型常駐GPU記憶體：所有模型（Whisper、LLM、Flow）預載入並快取
- 🔧 修復Flow模型包裝：正確整合Token2Wav實現token2wav_with_cache
- 🎤 增強Whisper整合：支援skip_whisper參數的自動轉錄
- ✅ 完整API測試覆蓋：驗證所有10個API端點（標準TTS、串流、voice_id、上傳）
- 🚀 生產就緒：穩定效能，生成時間穩定在2-3秒

### v2.0.0 (2025-12-12)
- 🚀 SSE串流TTS（伺服器推送事件）
- ⚡ 非同步最佳化的預生成架構
- 🎵 即時音訊區塊傳輸
- 🔄 FastAPI框架遷移
- 📡 標準和串流TTS雙模式
- 🎯 生產就緒的串流管線

### v1.0.0 (2025-12-12)
- ✨ 初始增強版本發布
- 🌐 即時進度的 Web UI
- 🔌 REST API 與 Swagger 文件
- 🎤 Whisper 自動轉錄
- 🐳 一體化 Docker 映像（20.5GB）
- ⚡ ONNX Runtime 的 cuDNN 9 支援
- 💾 主機掛載儲存
- 🔧 進階參數控制
- 🤖 MCP 伺服器整合

## 📄 授權

Apache License 2.0 - 詳見 [LICENSE](LICENSE)

## 🙏 致謝

- [GLM-TTS](https://github.com/zai-org/GLM-TTS) - 原始 TTS 模型
- [OpenAI Whisper](https://github.com/openai/whisper) - 語音識別
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) - 前端框架

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/GLM-TTS-Enhanced&type=Date)](https://star-history.com/#neosun100/GLM-TTS-Enhanced)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**由 GLM-TTS 增強團隊用 ❤️ 製作**
