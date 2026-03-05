# AnotherMe - AI Avatar Platform

| | Frontend | Chat Server | TTS Server | Lipsync Server |
|:---:|:---:|:---:|:---:|:---:|
| **Lint** | [![Lint Frontend](https://github.com/Rx-K8/AnotherMe/actions/workflows/lint-frontend.yml/badge.svg)](https://github.com/Rx-K8/AnotherMe/actions/workflows/lint-frontend.yml) | [![Lint Chat Server](https://github.com/Rx-K8/AnotherMe/actions/workflows/lint-chat-server.yml/badge.svg)](https://github.com/Rx-K8/AnotherMe/actions/workflows/lint-chat-server.yml) | [![Lint TTS Server](https://github.com/Rx-K8/AnotherMe/actions/workflows/lint-tts-server.yml/badge.svg)](https://github.com/Rx-K8/AnotherMe/actions/workflows/lint-tts-server.yml) | [![Lint Lipsync Server](https://github.com/Rx-K8/AnotherMe/actions/workflows/lint-lipsync-server.yml/badge.svg)](https://github.com/Rx-K8/AnotherMe/actions/workflows/lint-lipsync-server.yml) |
| **Test** | - | [![Test Chat Server](https://github.com/Rx-K8/AnotherMe/actions/workflows/test-chat-server.yml/badge.svg)](https://github.com/Rx-K8/AnotherMe/actions/workflows/test-chat-server.yml) | [![Test TTS Server](https://github.com/Rx-K8/AnotherMe/actions/workflows/test-tts-server.yml/badge.svg)](https://github.com/Rx-K8/AnotherMe/actions/workflows/test-tts-server.yml) | [![Test Lipsync Server](https://github.com/Rx-K8/AnotherMe/actions/workflows/test-lipsync-server.yml/badge.svg)](https://github.com/Rx-K8/AnotherMe/actions/workflows/test-lipsync-server.yml) |
| **Coverage** | - | [![Chat Server Coverage](https://coverage-badge.samuelcolvin.workers.dev/Rx-K8/AnotherMe.svg?match=chat-server)](https://coverage-badge.samuelcolvin.workers.dev/redirect/Rx-K8/AnotherMe?match=chat-server) | [![TTS Server Coverage](https://coverage-badge.samuelcolvin.workers.dev/Rx-K8/AnotherMe.svg?match=tts-server)](https://coverage-badge.samuelcolvin.workers.dev/redirect/Rx-K8/AnotherMe?match=tts-server) | [![Lipsync Server Coverage](https://coverage-badge.samuelcolvin.workers.dev/Rx-K8/AnotherMe.svg?match=lipsync-server)](https://coverage-badge.samuelcolvin.workers.dev/redirect/Rx-K8/AnotherMe?match=lipsync-server) |

## 概要

AnotherMe は、LLM によるチャット応答・音声合成・リップシンク動画生成を組み合わせた AI アバタープラットフォームです。4 つのサービスをモノレポで管理しています。

```
ユーザー入力 → Chat Server → テキスト応答
                                ↓
                           TTS Server → 音声生成
                                ↓
                        Lipsync Server → リップシンク動画生成
                                ↓
                         Frontend → アバター動画再生
```

## プロジェクト構成

```
AnotherMeProject/
├── frontend/                     # React 19 + TypeScript (Vite, port 5173)
├── chat-server/                  # FastAPI チャットサーバー (Python 3.13, CUDA 12.8, port 8000)
├── tts-server/                   # FastAPI TTSサーバー (Python 3.12, CUDA 12.4, port 8001)
├── lipsync-server/               # FastAPI リップシンクサーバー (Python 3.10, CUDA 11.8, port 8002)
│   └── submodules/MuseTalk/      # MuseTalk (git submodule)
├── scripts/                      # セットアップ・開発スクリプト
├── docs/                         # ドキュメント・リリースノート
├── pyproject.toml                # Ruff / MyPy 統一設定
├── .pre-commit-config.yaml       # Pre-commit フック設定
└── .github/                      # CI/CD ワークフロー
```

## 前提条件

| ツール | バージョン | 用途 |
|--------|-----------|------|
| Node.js | 20+ | Frontend |
| Python | 3.13 | Chat Server |
| Python | 3.12 | TTS Server |
| Python | 3.10 | Lipsync Server |
| [uv](https://docs.astral.sh/uv/) | 最新 | Python パッケージ管理 |
| NVIDIA GPU + CUDA | 11.8 / 12.4 / 12.8 | 推論（サービスにより異なる） |
| Git | 最新 | サブモジュール管理 |

```bash
# uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> Python の各バージョンは `uv python install` で自動インストールされます。

## クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/Rx-K8/AnotherMe.git
cd AnotherMe
git submodule update --init --recursive
```

### 2. セットアップ

```bash
# ローカル（GPU 環境）
./scripts/setup.sh

# CI（CPU-only PyTorch）
./scripts/setup.sh --ci
```

> `setup.sh` は Frontend・Chat Server・TTS Server の依存をインストールします。
> Lipsync Server は追加セットアップが必要です（[Lipsync Server の起動](#lipsync-server)を参照）。

### 3. 環境変数の設定

```bash
cp frontend/.env.example frontend/.env
cp chat-server/.env.example chat-server/.env
cp tts-server/.env.example tts-server/.env
cp lipsync-server/.env.example lipsync-server/.env
```

必要に応じて各 `.env` ファイルを編集してください（詳細は[環境変数](#環境変数)を参照）。

## サービスの起動

### Frontend

```bash
cd frontend
npm run dev
```

- URL: http://localhost:5173
- モックモード: `.env` で `VITE_USE_MOCK_API=true`（デフォルト）に設定するとバックエンド不要で動作確認できます

### Chat Server

```bash
cd chat-server
uv run uvicorn app.main:app --reload --port 8000
```

- API ドキュメント: http://localhost:8000/docs
- 初回起動時に Hugging Face からモデルをダウンロードします

### TTS Server

```bash
cd tts-server
uv run uvicorn app.main:app --reload --port 8001
```

- API ドキュメント: http://localhost:8001/docs
- 初回起動時に Qwen3-TTS モデルをダウンロードします

### Lipsync Server

Lipsync Server は MuseTalk と OpenMMLab の依存があり、追加セットアップが必要です。

#### 依存のインストール

```bash
cd lipsync-server

# Python パッケージ
uv sync --group dev

# OpenMMLab（GPU 環境必須）
.venv/bin/mim install mmengine mmcv==2.0.1 mmdet==3.1.0 mmpose==1.1.0

# chumpy（mmpose の依存）
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
.venv/bin/pip install chumpy --no-build-isolation
```

#### モデルの重みのダウンロード

```bash
bash download_weights.sh
```

#### 起動

`uv run` は lockfile にないパッケージ（mmcv 等）を削除するため、`.venv/bin/uvicorn` を直接使用します。

```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002
```

- API ドキュメント: http://localhost:8002/docs
- デモ UI: `ENABLE_DEMO=true` を設定すると `/demo` にテスト用 UI が表示されます

> 詳細なトラブルシューティングは [lipsync-server/README.md](lipsync-server/README.md) を参照してください。

## API リファレンス

各サービスの `/docs` で Swagger UI を利用できます。

### Chat Server (`http://localhost:8000`)

| Method | エンドポイント | 説明 |
|--------|---------------|------|
| POST | `/api/chat/completions` | チャット応答の生成（SSE streaming 対応） |
| GET | `/api/health` | ヘルスチェック |

### TTS Server (`http://localhost:8001`)

| Method | エンドポイント | 説明 |
|--------|---------------|------|
| POST | `/api/tts/voice-clone` | Voice Clone 音声合成（multipart/form-data） |
| GET | `/api/health/` | ヘルスチェック |

### Lipsync Server (`http://localhost:8002`)

| Method | エンドポイント | 説明 |
|--------|---------------|------|
| POST | `/api/lipsync/generate` | リップシンク動画生成（multipart/form-data） |
| GET | `/api/health/` | ヘルスチェック |

## 環境変数

### Frontend

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `VITE_USE_MOCK_API` | `true` | `true` でモック API を使用（バックエンド不要） |
| `VITE_CHAT_API_BASE_URL` | `http://localhost:8000` | Chat Server の URL |
| `VITE_TTS_API_BASE_URL` | `http://localhost:8001` | TTS Server の URL |
| `VITE_LIPSYNC_API_BASE_URL` | `http://localhost:8002` | Lipsync Server の URL |

### Chat Server

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `APP_NAME` | `AnotherMe Chat Server` | アプリケーション名 |
| `LLM_MODEL_NAME` | `Qwen/Qwen3-4B-Instruct-2507` | 使用する LLM モデル名 |
| `SERVER_HOST` | `0.0.0.0` | ホスト |
| `SERVER_PORT` | `8000` | ポート |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | 許可するオリジン（JSON 配列） |

### TTS Server

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `ENABLE_DEMO` | `false` | デモ UI の有効化 |
| `SERVER_HOST` | `0.0.0.0` | ホスト |
| `SERVER_PORT` | `8001` | ポート |
| `CORS_ORIGINS` | `["*"]` | 許可するオリジン（JSON 配列） |

### Lipsync Server

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `SERVER_HOST` | `0.0.0.0` | ホスト |
| `SERVER_PORT` | `8002` | ポート |
| `CORS_ORIGINS` | `["*"]` | 許可するオリジン（JSON 配列） |
| `GPU_DEVICE` | `cuda:2` | 使用する GPU デバイス |
| `MAX_AUDIO_SIZE_MB` | `10` | 最大音声ファイルサイズ（MB） |
| `MAX_VIDEO_SIZE_MB` | `50` | 最大動画ファイルサイズ（MB） |

## 開発

### リンティング

```bash
# Frontend
cd frontend && npm run lint

# Python サーバー（各ディレクトリで実行）
cd chat-server && uv run ruff check .
cd tts-server && uv run ruff check .
cd lipsync-server && uv run ruff check .

# 全プロジェクト一括
./scripts/lint-all.sh
```

### フォーマット

```bash
# Frontend
cd frontend && npm run format

# Python サーバー
cd chat-server && uv run ruff format .
cd tts-server && uv run ruff format .
cd lipsync-server && uv run ruff format .

# 全プロジェクト一括
./scripts/format-all.sh
```

### 型チェック

```bash
cd chat-server && uv run mypy app/
cd tts-server && uv run mypy app/
cd lipsync-server && uv run mypy app/
```

### テスト

```bash
# Frontend
cd frontend && npm run test

# Chat Server
cd chat-server && uv run pytest --cov

# TTS Server
cd tts-server && uv run pytest --cov

# Lipsync Server（GPU 不要テスト）
cd lipsync-server && uv run pytest -m "not gpu" --cov

# Lipsync Server（GPU テスト - .venv/bin/ を直接使用）
cd lipsync-server && .venv/bin/pytest -m gpu -v

# 全プロジェクト一括
./scripts/test-all.sh
```

### Pre-commit Hooks

セットアップ時に自動インストールされます。以下を実行します:

- ファイルサイズ・YAML・TOML・JSON チェック
- Ruff（lint + format）— Python コード
- Biome check — TypeScript コード

## 技術スタック

| | Frontend | Chat Server | TTS Server | Lipsync Server |
|---|---|---|---|---|
| 言語 | TypeScript | Python 3.13 | Python 3.12 | Python 3.10 |
| フレームワーク | React 19 + Vite | FastAPI | FastAPI | FastAPI |
| AI / ML | - | Gemma-3, Qwen3 | Qwen3-TTS | MuseTalk |
| GPU | - | CUDA 12.8 | CUDA 12.4 | CUDA 11.8 |
| パッケージ管理 | npm | uv | uv | uv + mim |
| リンティング | Biome | Ruff | Ruff | Ruff |
| テスト | Vitest | pytest | pytest | pytest |
| 型チェック | TypeScript | MyPy | MyPy | MyPy |

## CI/CD

GitHub Actions でコンポーネントごとに自動実行されます。

### コンポーネント別ワークフロー

変更されたコンポーネントに対して自動実行:

- **Lint Frontend** — `frontend/` 変更時
- **Lint Chat Server** — `chat-server/` 変更時
- **Lint TTS Server** — `tts-server/` 変更時
- **Lint Lipsync Server** — `lipsync-server/` 変更時
- **Test Chat Server** — `chat-server/` 変更時
- **Test TTS Server** — `tts-server/` 変更時
- **Test Lipsync Server** — `lipsync-server/` 変更時

### モノレポ横断ワークフロー

- **Labels** — PR に自動でコンポーネントラベルを付与
- **Latest Changes** — リリースノートを自動更新
- **Coverage Report** — テストカバレッジを Smokeshow で可視化

### パスフィルタリング

以下のファイル変更時にもワークフローがトリガーされます:

- ルートの `pyproject.toml` — 全 Python プロジェクトの lint 設定に影響
- `.pre-commit-config.yaml` — Pre-commit フック設定
- `scripts/lint-all.sh`, `scripts/test-all.sh` — 統合スクリプト
- 各ワークフローファイル自体の変更

## ドキュメント

- [frontend/README.md](frontend/README.md) — Frontend
- [chat-server/README.md](chat-server/README.md) — Chat Server
- [tts-server/README.md](tts-server/README.md) — TTS Server
- [lipsync-server/README.md](lipsync-server/README.md) — Lipsync Server（セットアップ詳細・トラブルシューティング）
- [docs/release-notes.md](docs/release-notes.md) — リリースノート

## ライセンス

[Your License Here]
