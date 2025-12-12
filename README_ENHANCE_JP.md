[English](README_ENHANCE.md) | [简体中文](README_ENHANCE_CN.md) | [繁體中文](README_ENHANCE_TW.md) | [日本語](README_ENHANCE_JP.md)

# GLM-TTS Enhanced：本番環境対応 TTS サービスと Web UI

[![Docker Hub](https://img.shields.io/docker/v/neosun/glm-tts?label=Docker%20Hub)](https://hub.docker.com/r/neosun/glm-tts)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://www.python.org/)

[GLM-TTS](https://github.com/zai-org/GLM-TTS) の強化版で、Web UI、REST API、自動文字起こし、Docker デプロイメントなどの本番環境対応機能を提供します。

## ✨ 強化機能

### 🎯 コア機能強化
- **🌐 Web UI**：リアルタイム進捗追跡を備えたモダンなレスポンシブインターフェース
- **🔌 REST API**：Swagger ドキュメント付きの完全な API
- **🎤 自動文字起こし**：Whisper 統合による参照テキストの自動生成
- **📊 リアルタイム進捗**：SSE ベースの進捗ストリーミングとタイミング情報
- **🐳 Docker 対応**：すべての依存関係がプリインストールされたオールインワン Docker イメージ
- **⚡ GPU 最適化**：適切な GPU デバイスマッピングと cuDNN 9 サポート
- **💾 永続ストレージ**：ファイル管理のためのホストマウントディレクトリ
- **🔧 高度な制御**：Temperature、Top-p、サンプリング戦略パラメータ

### 🆕 新機能
- **Whisper 自動文字起こし**：参照テキストを空白のままにすると音声から自動検出
- **進捗追跡**：経過時間表示付きのリアルタイム生成進捗
- **高度なパラメータ**：出力品質を微調整するための実験的コントロール
- **改善されたストレージ**：ファイルはホストマシンの `/tmp/glm-tts-voices` に保存
- **cuDNN 9 サポート**：完全な ONNX Runtime GPU アクセラレーション
- **オールインワンイメージ**：すべてのモデルを含む 20.5GB の Docker イメージ

## 🚀 クイックスタート

### 方法1：Docker（推奨）

オールインワンイメージをプルして実行：

```bash
# イメージをプル
docker pull neosun/glm-tts:all-in-one

# 一時ディレクトリを作成
mkdir -p /tmp/glm-tts-voices
chmod 777 /tmp/glm-tts-voices

# GPU 0 で実行（必要に応じてデバイス ID を変更）
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

Web UI にアクセス：`http://localhost:8080`

### 方法2：Docker Compose

`docker-compose.yml` を作成：

```yaml
version: '3.8'

services:
  glm-tts:
    image: neosun/glm-tts:all-in-one
    container_name: glm-tts
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=0  # ここで GPU ID を変更
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
              device_ids: ['0']  # ここで GPU ID を変更
              capabilities: [gpu]
```

サービスを起動：

```bash
docker-compose up -d
```

### 方法3：手動インストール

**前提条件：**
- Python 3.10 - 3.12
- CUDA 12.1+
- cuDNN 9
- NVIDIA GPU 16GB+ VRAM

**インストール手順：**

```bash
# リポジトリをクローン
git clone https://github.com/neosun100/GLM-TTS-Enhanced.git
cd GLM-TTS-Enhanced

# 依存関係をインストール
pip install -r requirements.txt
pip install flask flasgger flask-cors onnxruntime-gpu openai-whisper

# モデルをダウンロード
mkdir -p ckpt
huggingface-cli download zai-org/GLM-TTS --local-dir ckpt

# サーバーを起動
python server.py
```

## 📖 使用方法

### Web インターフェース

1. ブラウザで `http://localhost:8080` を開く
2. 参照音声ファイルをアップロード（3-10秒）
3. 合成するテキストを入力（または参照テキストを空白のままにして自動文字起こし）
4. 「音声を生成」をクリックしてリアルタイム進捗を確認
5. 生成された音声をダウンロード

### REST API

**音声生成：**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=こんにちは、これはテストです。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参照音声のテキスト内容" \
  -F "temperature=0.8" \
  -F "top_p=0.9" \
  -F "sampling_strategy=balanced"
```

**API ドキュメント：**

`http://localhost:8080/apidocs` にアクセスしてインタラクティブな Swagger ドキュメントを表示。

### 高度なパラメータ

- **Temperature** (0.1-1.5)：ランダム性を制御（高いほど多様化）
- **Top-p** (0.5-1.0)：ニュークリアスサンプリング閾値
- **サンプリング戦略**：
  - `fast`：高速生成、品質は低め
  - `balanced`：デフォルト、品質/速度のバランス
  - `quality`：最高品質、生成は遅め
- **Whisper をスキップ**：自動文字起こしを無効にして処理を高速化

## 🏗️ アーキテクチャ

### システムコンポーネント

```
┌─────────────────┐
│   Web UI        │
│  (HTML/JS)      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Flask サーバー │
│  (server.py)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  TTS エンジン   │
│ (tts_engine.py) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Whisper│  │GLM-TTS│
│ モデル│  │ モデル│
└───────┘  └───────┘
```

### 強化されたファイル

| ファイル | 目的 |
|---------|------|
| `server.py` | SSE 進捗ストリーミング付き Flask REST API |
| `tts_engine.py` | Whisper 統合付き TTS 推論エンジン |
| `Dockerfile` | cuDNN 9 を含むマルチステージビルド |
| `docker-compose.yml` | 本番デプロイメント設定 |
| `.gitignore` | 機密データを除外するように強化 |

## 🔧 設定

### 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `PORT` | 8080 | サーバーポート |
| `TEMP_DIR` | `/tmp/glm-tts-voices` | 一時ファイルストレージ |
| `GPU_IDLE_TIMEOUT` | 60 | GPU アイドルタイムアウト（秒） |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU デバイス ID |

### GPU 選択

特定の GPU を使用（例：GPU 2）：

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

## 📊 パフォーマンス

- **モデルサイズ**：20.5GB（オールインワンイメージ）
- **VRAM 使用量**：推論時約 12GB
- **生成速度**：10秒の音声に2-5秒
- **Whisper オーバーヘッド**：自動文字起こしで2-3秒追加

## 🛠️ トラブルシューティング

### よくある問題

**1. CUDA メモリ不足**
- バッチサイズを減らすか、より多くの VRAM を持つ GPU を使用
- 他の GPU 集約型アプリケーションを閉じる

**2. cuDNN バージョンの不一致**
- cuDNN 9 がインストールされていることを確認（Docker イメージに含まれています）
- 確認：`ldconfig -p | grep cudnn`

**3. 生成が遅い**
- GPU が使用されていることを確認：`nvidia-smi`
- NVIDIA_VISIBLE_DEVICES が GPU と一致しているか確認

**4. Whisper が失敗**
- 音声がクリアでサポートされている形式であることを確認
- `skip_whisper=true` を使用して自動文字起こしをバイパス

## 📦 ソースからのビルド

```bash
# Docker イメージをビルド
docker build -t glm-tts:custom .

# レジストリにプッシュ
docker tag glm-tts:custom your-registry/glm-tts:latest
docker push your-registry/glm-tts:latest
```

## 🤝 貢献

貢献を歓迎します！以下の手順で：

1. リポジトリをフォーク
2. 機能ブランチを作成
3. 変更をコミット
4. ブランチにプッシュ
5. プルリクエストを開く

## 📝 変更履歴

### v1.0.0 (2025-12-12)
- ✨ 初回強化版リリース
- 🌐 リアルタイム進捗付き Web UI を追加
- 🔌 Swagger ドキュメント付き REST API
- 🎤 Whisper 自動文字起こし統合
- 🐳 オールインワン Docker イメージ（20.5GB）
- ⚡ ONNX Runtime 用 cuDNN 9 サポート
- 💾 永続化のためのホストマウントストレージ
- 🔧 高度なパラメータ制御

## 📄 ライセンス

このプロジェクトは Apache License 2.0 の下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 🙏 謝辞

- [GLM-TTS](https://github.com/zai-org/GLM-TTS) - オリジナル TTS モデル
- [OpenAI Whisper](https://github.com/openai/whisper) - 音声認識
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) - フロントエンドフレームワーク

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/GLM-TTS-Enhanced&type=Date)](https://star-history.com/#neosun100/GLM-TTS-Enhanced)

## 📱 フォローする

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

**GLM-TTS Enhanced チームが ❤️ を込めて作成**
