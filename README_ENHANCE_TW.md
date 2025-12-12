[English](README_ENHANCE.md) | [简体中文](README_ENHANCE_CN.md) | [繁體中文](README_ENHANCE_TW.md) | [日本語](README_ENHANCE_JP.md)

# GLM-TTS 增強版：生產級 TTS 服務與 Web 介面

[![Docker Hub](https://img.shields.io/docker/v/neosun/glm-tts?label=Docker%20Hub)](https://hub.docker.com/r/neosun/glm-tts)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://www.python.org/)

[GLM-TTS](https://github.com/zai-org/GLM-TTS) 的增強版本，提供生產級功能，包括 Web UI、REST API、自動轉錄和 Docker 部署。

## ✨ 增強功能

### 🎯 核心增強
- **🌐 Web 介面**：現代化響應式介面，即時進度追蹤
- **🔌 REST API**：完整的 API 與 Swagger 文件
- **🎤 自動轉錄**：整合 Whisper 自動生成參考文字
- **📊 即時進度**：基於 SSE 的進度串流傳輸與計時資訊
- **🐳 Docker 就緒**：預裝所有依賴的一體化 Docker 映像
- **⚡ GPU 優化**：正確的 GPU 裝置映射和 cuDNN 9 支援
- **💾 持久化儲存**：掛載主機目錄進行檔案管理
- **🔧 進階控制**：Temperature、Top-p 和採樣策略參數

### 🆕 新增特性
- **Whisper 自動轉錄**：參考文字留空時自動從音訊識別
- **進度追蹤**：即時生成進度與耗時顯示
- **進階參數**：實驗性控制用於微調輸出品質
- **改進儲存**：檔案儲存在主機 `/tmp/glm-tts-voices`
- **cuDNN 9 支援**：完整的 ONNX Runtime GPU 加速
- **一體化映像**：20.5GB Docker 映像包含所有模型

## 🚀 快速開始

### 方式一：Docker（推薦）

拉取並執行一體化映像：

```bash
# 拉取映像
docker pull neosun/glm-tts:all-in-one

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
  neosun/glm-tts:all-in-one
```

存取 Web 介面：`http://localhost:8080`

### 方式二：Docker Compose

建立 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  glm-tts:
    image: neosun/glm-tts:all-in-one
    container_name: glm-tts
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0  # 在此更改 GPU ID
      - PORT=8080
      - GPU_IDLE_TIMEOUT=60
      - TEMP_DIR=/tmp/glm-tts-voices
    ports:
      - "8080:8080"
    volumes:
      - /tmp/glm-tts-voices:/tmp/glm-tts-voices
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']  # 在此更改 GPU ID
              capabilities: [gpu]
```

啟動服務：

```bash
docker-compose up -d
```

### 方式三：手動安裝

**前置要求：**
- Python 3.10 - 3.12
- CUDA 12.1+
- cuDNN 9
- NVIDIA GPU 16GB+ 顯存

**安裝步驟：**

```bash
# 複製儲存庫
git clone https://github.com/neosun100/GLM-TTS-Enhanced.git
cd GLM-TTS-Enhanced

# 安裝依賴
pip install -r requirements.txt
pip install flask flasgger flask-cors onnxruntime-gpu openai-whisper

# 下載模型
mkdir -p ckpt
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt

# 啟動伺服器
python server.py
```

## 📖 使用方法

### Web 介面

1. 在瀏覽器中開啟 `http://localhost:8080`
2. 上傳參考音訊檔案（3-10 秒）
3. 輸入要合成的文字（或留空參考文字以自動轉錄）
4. 點擊「生成語音」並觀察即時進度
5. 下載生成的音訊

### REST API

**生成語音：**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=你好，這是一個測試。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=參考音訊的文字內容" \
  -F "temperature=0.8" \
  -F "top_p=0.9" \
  -F "sampling_strategy=balanced"
```

**API 文件：**

存取 `http://localhost:8080/apidocs` 檢視互動式 Swagger 文件。

### 進階參數

- **Temperature** (0.1-1.5)：控制隨機性（越高越多樣化）
- **Top-p** (0.5-1.0)：核採樣閾值
- **採樣策略**：
  - `fast`：快速生成，品質較低
  - `balanced`：預設，品質/速度平衡
  - `quality`：最佳品質，生成較慢
- **跳過 Whisper**：停用自動轉錄以加快處理速度

## 🏗️ 架構

### 系統元件

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

### 增強檔案

| 檔案 | 用途 |
|------|------|
| `server.py` | Flask REST API 與 SSE 進度流 |
| `tts_engine.py` | TTS 推理引擎與 Whisper 整合 |
| `Dockerfile` | 多階段建置與 cuDNN 9 |
| `docker-compose.yml` | 生產部署設定 |
| `.gitignore` | 增強以排除敏感資料 |

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

**Docker Run：**
```bash
docker run -e NVIDIA_VISIBLE_DEVICES=2 ...
```

**Docker Compose：**
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

- **模型大小**：20.5GB（一體化映像）
- **顯存使用**：推理時約 12GB
- **生成速度**：10 秒音訊需 2-5 秒
- **Whisper 開銷**：自動轉錄增加 2-3 秒

## 🛠️ 故障排除

### 常見問題

**1. CUDA 記憶體不足**
- 減少批次大小或使用更大顯存的 GPU
- 關閉其他 GPU 密集型應用程式

**2. cuDNN 版本不符**
- 確保安裝 cuDNN 9（Docker 映像已包含）
- 檢查：`ldconfig -p | grep cudnn`

**3. 生成緩慢**
- 驗證正在使用 GPU：`nvidia-smi`
- 檢查 NVIDIA_VISIBLE_DEVICES 是否符合您的 GPU

**4. Whisper 失敗**
- 確保音訊清晰且格式受支援
- 使用 `skip_whisper=true` 繞過自動轉錄

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

### v1.0.0 (2025-12-12)
- ✨ 初始增強版本發布
- 🌐 新增即時進度的 Web UI
- 🔌 REST API 與 Swagger 文件
- 🎤 Whisper 自動轉錄整合
- 🐳 一體化 Docker 映像（20.5GB）
- ⚡ ONNX Runtime 的 cuDNN 9 支援
- 💾 主機掛載儲存以實現持久化
- 🔧 進階參數控制

## 📄 授權

本專案採用 Apache License 2.0 授權 - 詳見 [LICENSE](LICENSE) 檔案。

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
