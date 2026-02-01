## Dockerイメージのビルドと起動

### 1. Dockerイメージのビルド

```
docker build -t miyalab/anotherme-chat-server:12.8.1-cudnn-runtime-ubuntu22.04 .
```

### 2. Dockerコンテナの起動

```
docker run --rm -p 8000:8000 --gpus '"device=0"' --env-file .env  miyalab/anotherme-chat-server:12.8.1-cudnn-runtime-ubuntu22.04
```

## 🔑 Hugging Faceアクセスのための認証設定

`google/gemma-3-4b-it`のような**アクセス制限付き（Gated Repo）のモデル**を使用する場合、Hugging Faceの認証が必要です。以下の手順に従って、アクセストークンを取得し、環境にログインしてください。

### 1\. モデルへのアクセス権限の取得

1.  Hugging Faceにログインします。
2.  対象モデルのページ（例：`google/gemma-3-4b-it`）にアクセスします。
3.  利用規約を確認し、\*\*アクセスをリクエスト（同意）\*\*して、モデルへのアクセス権限を取得してください。

### 2\. アクセストークンの生成

1.  Hugging Faceの「Settings」→「Access Tokens」ページに移動します。
2.  新しいトークンを作成します（**New token**）。
3.  **Name**（トークン名）を入力します（例：`gemma-model-access`）。
4.  **Role**（権限）は、モデルのダウンロードと利用のために、**`Read`** を選択してください。
5.  トークンを生成し、表示された文字列（`hf_...`で始まる）をコピーします。

### 3\. 環境へのログイン（認証）

コードを実行する環境（ターミナル）で、コピーしたトークンを使用してログインします。

```bash
huggingface-cli login
```

プロンプトが表示されたら、コピーしたアクセストークンを貼り付けて認証を完了させてください。

> ℹ️ **注意:**
> ログイン時、「`Add token as git credential?`」と聞かれた場合は、「Yes」を選択すると、今後のリポジトリアクセス時の認証が自動化されます。

上記の手順が完了した後、本アプリケーションの起動を再試行してください。
