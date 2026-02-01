# AnotherMe - AI Avatar Platform

A monorepo containing the full AnotherMe platform: Frontend, Chat Server, and TTS Server.

## Project Structure

```
AnotherMeProject/
├── frontend/        # React/TypeScript web application
├── chat-server/     # FastAPI chat server with LLM
├── tts-server/      # FastAPI TTS server with Qwen3-TTS
├── scripts/         # Development and build scripts
├── docs/            # Documentation
└── .github/         # CI/CD workflows
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+ (for TTS Server) / 3.13 (for Chat Server)
- uv (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- NVIDIA GPU with CUDA support (for inference)

### Setup

```bash
# One-command setup
./scripts/setup.sh
```

### Running Services

#### Frontend
```bash
cd frontend
npm run dev
```
Access at: http://localhost:5173

#### Chat Server
```bash
cd chat-server
uv run uvicorn app.main:app --reload --port 8000
```
API docs at: http://localhost:8000/docs

#### TTS Server
```bash
cd tts-server
uv run uvicorn app.main:app --reload --port 8001
```
API docs at: http://localhost:8001/docs

## Development

### Linting

```bash
# Lint all projects
./scripts/lint-all.sh

# Format all projects
./scripts/format-all.sh
```

### Testing

```bash
# Run all tests
./scripts/test-all.sh
```

### Pre-commit Hooks

Pre-commit hooks are automatically installed during setup. They will:
- Check file sizes, YAML, TOML, JSON
- Run Ruff (lint + format) on Python code
- Run Biome check on TypeScript code

## Tech Stack

### Frontend
- React 19 + TypeScript
- Vite
- TanStack Router
- Tailwind CSS
- Biome (linting/formatting)

### Chat Server
- Python 3.13
- FastAPI
- PyTorch 2.9.0 (CUDA 12.8)
- Transformers (Gemma-3, Qwen3)
- uv package manager

### TTS Server
- Python 3.12
- FastAPI
- Qwen3-TTS
- PyTorch (CUDA 12.4)
- uv package manager

## CI/CD

このモノレポでは、以下のGitHub Actionsワークフローを使用しています。

### コンポーネント別ワークフロー

変更されたコンポーネントに対して自動実行されます：

- **Lint Frontend** - フロントエンドのlint（`frontend/` 変更時に自動実行）
- **Lint Chat Server** - チャットサーバーのlint（`chat-server/` 変更時に自動実行）
- **Lint TTS Server** - TTSサーバーのlint（`tts-server/` 変更時に自動実行）
- **Test TTS Server** - TTSサーバーのテスト（`tts-server/` 変更時に自動実行）

### モノレポ横断ワークフロー

すべてのコンポーネントに影響する機能：

- **Labels** - PRに自動でコンポーネントラベル（frontend/chat-server/tts-server/monorepo）を付与
- **Latest Changes** - コンポーネント別のrelease-notes.mdを自動更新
- **Coverage Report** - テストカバレッジを可視化（Smokeshow）

### 統合ワークフロー（手動実行）

全プロジェクトを一括で検証：

- **Lint All Projects** - 全プロジェクトのlintを一括実行
- **Test All Projects** - 全プロジェクトのテストを一括実行

### パスフィルタリング

ワークフローは以下のファイル変更時にもトリガーされます：

- ルートの `pyproject.toml` - 全Pythonプロジェクトのlint設定に影響
- `.pre-commit-config.yaml` - pre-commitフック設定
- `scripts/lint-all.sh`, `scripts/test-all.sh` - 統合スクリプト
- 各ワークフローファイル自体の変更

### Issue/PRテンプレート

- **バグ報告** - コンポーネントを選択してバグを報告
- **機能リクエスト** - コンポーネントを選択して新機能を提案
- **質問** - Discussionsで質問（コンポーネント選択可能）

## Documentation

- [frontend/README.md](frontend/README.md) - Frontend documentation
- [chat-server/README.md](chat-server/README.md) - Chat Server documentation
- [tts-server/README.md](tts-server/README.md) - TTS Server documentation

## License

[Your License Here]
