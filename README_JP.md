[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# GLM-TTS Enhanced：本番環境対応 TTS サービス

[![Docker Hub](https://img.shields.io/docker/v/neosun/glm-tts?label=Docker%20Hub)](https://hub.docker.com/r/neosun/glm-tts)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![Python](https://img.shields.io/badge/Python-3.10--3.12-blue.svg)](https://www.python.org/)

GLM-TTS の強化版で、本番環境対応機能を提供：Web UI、REST API、Whisper 自動文字起こし、Docker デプロイメント。

![GLM-TTS Enhanced UI](https://img.aws.xin/uPic/YD5e2C.png)

## ✨ 強化機能

### 🎯 コア機能強化
- **🌐 モダンな Web UI**：リアルタイム進捗追跡を備えたレスポンシブインターフェース
- **🔌 REST API**：`/apidocs` で Swagger ドキュメント付きの完全な API
- **🎤 Whisper 統合**：参照テキストが空の場合の自動音声文字起こし
- **📊 リアルタイム進捗**：SSE ベースのストリーミングと経過時間表示
- **🐳 オールインワン Docker**：すべてのモデルと依存関係を含む 23.6GB イメージ
- **⚡ GPU 最適化**：ONNX Runtime GPU アクセラレーション用 cuDNN 9 サポート
- **💾 永続ストレージ**：ファイル管理のためのホストマウントディレクトリ
- **🔧 高度な制御**：Temperature、Top-p、サンプリング戦略パラメータ
- **🤖 MCP サーバー**：AI エージェント統合用 Model Context Protocol サーバー

### 🆕 新機能
- Whisper 自動文字起こし（参照テキストを空白のまま）
- タイミング付きリアルタイム生成進捗
- 実験的な高度なパラメータ
- ホストの `/tmp/glm-tts-voices` にファイルを保存
- cuDNN 9 による完全な ONNX Runtime GPU アクセラレーション
- AI エージェントとのシームレスな統合のための MCP サーバー

## 🚀 クイックスタート（推奨）

### Docker の使用（オールインワンイメージ）

```bash
# 最新の v2.3.1 イメージをプル
docker pull neosun/glm-tts:all-in-one-fastapi-v2.3.1

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
  neosun/glm-tts:all-in-one-fastapi-v2.3.1
```

**Web UI にアクセス**：`http://localhost:8080`

### Docker Compose の使用

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

サービスを起動：
```bash
docker-compose up -d
```

## 📖 使用方法

### Web インターフェース

1. ブラウザで `http://localhost:8080` を開く
2. 参照音声ファイルをアップロード（3-10秒、WAV 形式）
3. 合成するテキストを入力
4. **オプション**：Whisper による自動文字起こしのため参照テキストを空白のまま
5. **オプション**：微調整のため「高度なパラメータ」を展開
6. 「音声を生成」をクリックしてリアルタイム進捗を確認
7. 生成された音声をダウンロード

### REST API

**音声生成：**

```bash
curl -X POST http://localhost:8080/api/tts \
  -F "text=こんにちは、これはテストです。" \
  -F "prompt_audio=@reference.wav" \
  -F "prompt_text=参照音声テキスト" \
  -F "temperature=0.8" \
  -F "top_p=0.9" \
  -F "sampling_strategy=balanced"
```

**API ドキュメント**：インタラクティブな Swagger ドキュメントは `http://localhost:8080/apidocs` にアクセス。

**ヘルスチェック：**
```bash
curl http://localhost:8080/health
```

### MCP サーバー統合

プロジェクトには AI エージェント統合用の MCP（Model Context Protocol）サーバーが含まれています：

```bash
# MCP サーバーを起動
python mcp_server.py

# AI エージェントで設定（例：Claude Desktop）
# 詳細は MCP_GUIDE.md を参照
```

### 高度なパラメータ

- **Temperature** (0.1-1.5)：ランダム性を制御（高いほど多様化）
- **Top-p** (0.5-1.0)：ニュークリアスサンプリング閾値
- **サンプリング戦略**：
  - `fast`：高速生成、品質は低め
  - `balanced`：デフォルト、品質/速度のバランス
  - `quality`：最高品質、生成は遅め
- **Whisper をスキップ**：処理を高速化するため自動文字起こしを無効化

## 🏗️ アーキテクチャ

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

### 強化されたコンポーネント

| コンポーネント | 説明 |
|---------------|------|
| `server.py` | SSE 進捗ストリーミング付き Flask REST API |
| `tts_engine.py` | Whisper 統合付き TTS 推論エンジン |
| `mcp_server.py` | AI エージェント統合用 MCP サーバー |
| `Dockerfile` | cuDNN 9 を含むマルチステージビルド |
| `docker-compose.yml` | 本番デプロイメント設定 |

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

```bash
docker run -e NVIDIA_VISIBLE_DEVICES=2 ...
```

または `docker-compose.yml` で：
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

- **モデルサイズ**：23.6GB（v2.3.1オールインワンイメージ）
- **VRAM 使用量**：推論時約 12GB
- **生成速度**：10秒の音声に2-3秒（v2.0.0より20-30倍高速）
- **Whisper オーバーヘッド**：自動文字起こしで2-3秒追加
- **起動時間**：約90秒（一度のモデル読み込み）
- **モデルキャッシュ**：すべてのモデルがGPUメモリに常駐し、即座に推論可能

## 🛠️ トラブルシューティング

### よくある問題

**CUDA メモリ不足**
- より多くの VRAM を持つ GPU を使用（16GB+ 推奨）
- 他の GPU アプリケーションを閉じる

**cuDNN バージョンの不一致**
- 提供されている Docker イメージを使用（cuDNN 9 含む）
- 確認：`ldconfig -p | grep cudnn`

**生成が遅い**
- GPU が使用されていることを確認：`nvidia-smi`
- NVIDIA_VISIBLE_DEVICES が GPU と一致しているか確認

**Whisper が失敗**
- 音声がクリアでサポートされている形式であることを確認
- `skip_whisper=true` を使用してバイパス

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

### v2.3.1 (2025-12-13)
- ⚡ **20-30倍のパフォーマンス向上**：推論時間が60秒から2-3秒に短縮
- 🏗️ アーキテクチャの刷新：TTSEngineでの直接モデル読み込み、subprocessオーバーヘッドの排除
- 💾 GPUメモリ常駐モデル：すべてのモデル（Whisper、LLM、Flow）を事前読み込みしキャッシュ
- 🔧 Flowモデルラッパーの修正：Token2Wavの適切な統合によるtoken2wav_with_cacheの実装
- 🎤 Whisper統合の強化：skip_whisperパラメータをサポートする自動文字起こし
- ✅ 完全なAPIテストカバレッジ：全10個のAPIエンドポイントを検証（標準TTS、ストリーミング、voice_id、アップロード）
- 🚀 本番環境対応：安定したパフォーマンス、2-3秒の一貫した生成時間

### v2.0.0 (2025-12-12)
- 🚀 SSEストリーミングTTS（サーバー送信イベント）
- ⚡ 非同期最適化のための事前生成アーキテクチャ
- 🎵 リアルタイムオーディオチャンク配信
- 🔄 FastAPIフレームワークへの移行
- 📡 標準およびストリーミングTTSのデュアルモード
- 🎯 本番環境対応のストリーミングパイプライン

### v1.0.0 (2025-12-12)
- ✨ 初回強化版リリース
- 🌐 リアルタイム進捗付き Web UI
- 🔌 Swagger ドキュメント付き REST API
- 🎤 Whisper 自動文字起こし
- 🐳 オールインワン Docker イメージ（20.5GB）
- ⚡ ONNX Runtime 用 cuDNN 9 サポート
- 💾 ホストマウントストレージ
- 🔧 高度なパラメータ制御
- 🤖 MCP サーバー統合

## 📄 ライセンス

Apache License 2.0 - 詳細は [LICENSE](LICENSE) を参照

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
