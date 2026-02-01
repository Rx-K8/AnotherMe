# AnotherMe TTS Server

Qwen3-TTS を使用したテキスト音声合成（TTS）サーバー。FastAPI ベースの REST API を提供。

## 技術スタック

- Python 3.12
- FastAPI + Uvicorn
- Qwen3-TTS (Qwen/Qwen3-TTS-12Hz-1.7B-Base)
- uv (パッケージ管理)

## 共通コマンド

```bash
# 依存関係のインストール
uv sync              # 本番環境
uv sync --group dev  # 開発環境

# サーバー起動
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001

# フォーマット（自動修正）
./scripts/format.sh

# リント・型チェック
./scripts/lint.sh
```

## コーディング規約

- **型ヒント**: すべての関数に必須（mypy strict モード）
- **Docstring**: Google 形式を使用
- **print文禁止**: ロギングを使用すること
- **行長**: 88文字（Ruff/Black 準拠）

## ブランチ戦略（Git Flow）

- `main`: 本番用（直接 push 禁止）
- `develop`: 開発メインブランチ
- `feature/*`: 新機能
- `bugfix/*`: バグ修正
- `refactor/*`: リファクタリング

### 開発フロー

1. `develop` から新しいブランチを作成
2. 変更をコミット
3. **必ず PR を作成して `develop` にマージ**（直接 push 禁止）
4. リリース時は `develop` から `main` へ PR を作成

## PR ラベル

| ラベル | 用途 |
|--------|------|
| `feature` | 新機能 |
| `bug` | バグ修正 |
| `refactor` | リファクタリング |
| `docs` | ドキュメント |
