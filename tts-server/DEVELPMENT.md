# 新規開発者向けオンボーディングガイド

このドキュメントでは、新しい開発者がこのプロジェクトに参加するにあたって理解しておくべき内容をまとめています。

## 📋 目次

- [プロジェクト概要](#プロジェクト概要)
- [開発環境のセットアップ](#開発環境のセットアップ)
- [開発ワークフロー](#開発ワークフロー)
- [コーディング規約](#コーディング規約)

---

## プロジェクト概要

このリポジトリは、新しいPythonプロジェクトを開始するためのテンプレートです。以下の機能が含まれています:

- **Ruff** による高速なリンティングとフォーマット
- **mypy** による静的型チェック
- **pre-commit** フックによる自動品質チェック
- **conda** による環境管理

---

## 開発環境のセットアップ

### 1. 必要な環境

- **Python 3.10** (condaで管理)
- **Git**
- **conda** (Anaconda または Miniconda)

### 2. condaのインストール

[Miniconda](https://docs.conda.io/en/latest/miniconda.html) または [Anaconda](https://www.anaconda.com/download) をインストールしてください。

```bash
# Miniconda (Linux)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### 3. Python環境のセットアップ

```bash
# 開発用環境の作成（ruff, mypyを含む）
conda env create -f environment-dev.yml

# 環境のアクティベート
conda activate anotherme_tts_dev
```

> **NOTE**: 本番環境用には `environment.yml` を使用してください:
> ```bash
> conda env create -f environment.yml
> conda activate anotherme_tts
> ```

### 4. pre-commitフックの設定

```bash
# pre-commitのインストール（環境に含まれていない場合）
pip install pre-commit

# フックの設定
pre-commit install
```

---

## 開発ワークフロー

### ブランチ戦略

Git Flowに基づいたブランチ戦略を採用しています:

- **main**: 本番環境用の安定ブランチ（直接pushは禁止）
- **develop**: 開発用のメインブランチ（PRベースで開発）
- **feature/\***: 新機能開発用
- **bugfix/\***: バグ修正用
- **refactor/\***: リファクタリング用

### 開発の流れ

1. **developブランチから新しいブランチを作成**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **プルリクエストを作成**
   ```bash
   git push origin feature/your-feature-name
   ```

   GitHub上でPRを作成し、以下のラベルを付けます:

### PRラベルの使い方

PRには必ず1つ以上のラベルを付けてください。ラベルに応じて以下の効果があります:

- **リリースノートに自動記録**される（developへのマージ時）

| ラベル | 絵文字 | 用途 |
|--------|--------|------|
| `feature` | ✨ | 新機能の追加 |
| `bug` | 🐛 | バグ修正 |
| `refactor` | ♻️ | リファクタリング |
| `docs` | 📝 | ドキュメントの変更 |
| `internal` | ⚙️ | 内部実装の変更（.github、scriptsなど） |
| `breaking` | 💥 | 破壊的変更 |
| `security` | 🔒 | セキュリティ修正 |
| `upgrade` | ⬆️ | 依存関係のアップグレード |

> **例**: 新機能を追加した場合は`feature`ラベルを付けると、PRタイトルが「✨ 機能名」のように自動更新されます

---

## コーディング規約

### 1. 型ヒント

すべての関数に型ヒントを付けてください:

```python
def calculate_total(items: list[int]) -> int:
    return sum(items)
```

### 2. Docstring

Google形式のDocstringを使用してください。
vscodeの拡張機能を利用すると便利です。

```python
def example_function(param1: str, param2: int) -> bool:
    """関数の簡潔な説明.

    Args:
        param1: 第1引数の説明
        param2: 第2引数の説明

    Returns:
        戻り値の説明

    Raises:
        ValueError: 発生する例外の説明
    """
    pass
```

### 3. コメント

TODOタグを使って作業を追跡できます。
vscodeの拡張機能を利用すると便利です。

- `# TODO: 実装予定の機能`
- `# FIXME: 修正が必要なコード`
- `# NOTE: 重要な注意事項`
- `# HACK: 一時的な回避策`
- `# BUG: 既知のバグ`

### 5. print文の禁止

本番コードでは`print()`の使用は禁止されています。代わりにロギングを使用してください:

---

## 参考リンク

- [conda Documentation](https://docs.conda.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pre-commit Documentation](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Welcome to the team! Happy coding! 🚀**
