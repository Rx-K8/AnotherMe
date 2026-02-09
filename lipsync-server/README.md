# AnotherMe Lipsync Server

MuseTalk を利用したリップシンク動画生成サーバー（FastAPI, Python 3.10, CUDA 11.8）。

## インストール

### uv 環境のセットアップ

```bash
# uv のインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 開発環境
cd lipsync-server
uv sync --group dev
```

### OpenMMLab のインストール（必須・GPU 環境のみ）

MuseTalk の顔ランドマーク検出に mmpose が必要。
mmcv / mmdet / mmpose は pip wheel の互換性の問題から `pyproject.toml` に含めておらず、`mim install` で別途インストールする。

```bash
# setuptools を固定（v82+ は pkg_resources を削除しており mmcv が動作しない）
uv pip install "setuptools<70"

# OpenMMLab のインストール
uv pip install openmim
uv run mim install mmengine mmcv==2.0.1 mmdet==3.1.0 mmpose==1.1.0
```

> **注意**: `uv sync` や `uv run` を実行すると、lockfile に存在しないパッケージ（mmcv 等）が削除される場合がある。
> GPU テストの実行時は `.venv/bin/pytest` を直接使用すること（後述）。

### chumpy のインストール（mmpose の依存）

chumpy のビルドには pip モジュールが必要だが、uv 環境には含まれていない場合がある。

```bash
# pip をブートストラップ
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python

# chumpy をインストール（ビルド分離を無効化）
.venv/bin/pip install chumpy --no-build-isolation
```

### MuseTalk サブモジュール

```bash
# サブモジュールの初期化（リポジトリルートで実行）
git submodule update --init lipsync-server/submodules/MuseTalk
```

モデルの重みは別途ダウンロードし、`submodules/MuseTalk/models/` に配置する。

```bash
cd submodules/MuseTalk
bash download_weights.sh
```

## サーバーの起動

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### デモ UI の有効化

環境変数 `ENABLE_DEMO=true` を設定すると `/demo` にテスト用 UI が表示される。

```bash
ENABLE_DEMO=true uv run uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## Docker イメージのビルドと起動

### Docker イメージのビルド

```bash
docker build -t nvidia-anotherme/lipsync-server:cu118-runtime .
```

### Docker コンテナの起動

モデルの重みはボリュームマウントで提供する（イメージには含まれない）。

```bash
docker run --rm -p 8002:8002 --gpus '"device=2"' \
  -v /path/to/MuseTalk/models:/app/submodules/MuseTalk/models \
  nvidia-anotherme/lipsync-server:cu118-runtime
```

## テスト

### 単体テスト + 統合テスト（GPU 不要）

```bash
uv run pytest -m "not gpu" --cov
```

### GPU テスト

`uv run` は lockfile にない手動インストールパッケージを削除するため、`.venv/bin/pytest` を直接使用する。

```bash
.venv/bin/pytest -m gpu -v
```

## 依存関係のトラブルシューティング

### `ModuleNotFoundError: No module named 'mmpose'`

mmpose は `pyproject.toml` に含まれていない。「OpenMMLab のインストール」の手順を参照。

### `ModuleNotFoundError: No module named 'pkg_resources'`

setuptools v82 以降は `pkg_resources` が削除されている。`setuptools<70` をインストールする。

```bash
uv pip install "setuptools<70"
```

### `uv run` 後に mmcv / mmpose が消える

`uv run` は lockfile と環境を同期するため、lockfile に存在しないパッケージを削除する。
GPU テストは `.venv/bin/pytest` を直接使用すること。

```bash
# NG: mmcv 等が削除される
uv run pytest -m gpu

# OK: 手動インストールしたパッケージが維持される
.venv/bin/pytest -m gpu -v
```

### `FileNotFoundError: './musetalk/utils/dwpose/...'`

MuseTalk の `preprocessing.py` がモジュールレベルで相対パスを使用しており、CWD が `submodules/MuseTalk/` でないと失敗する。
`musetalk_provider.py` の `_chdir_musetalk()` コンテキストマネージャーで対処済みだが、
MuseTalk を直接使う場合は CWD に注意すること。

### chumpy のビルドエラー (`No module named 'pip'`)

chumpy の `setup.py` がビルド時に pip を import する。uv 環境には pip が無いためエラーになる。
pip をブートストラップしてから `--no-build-isolation` でインストールする。

```bash
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
.venv/bin/pip install chumpy --no-build-isolation
```
