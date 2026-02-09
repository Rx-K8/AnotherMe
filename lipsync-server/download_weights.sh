#!/bin/bash
# MuseTalk モデル重みダウンロードスクリプト
# 公式 MuseTalk/download_weights.sh をベースに、lipsync-server 用に調整。
# サーバー起動前に実行すること。
#
# Usage:
#   cd lipsync-server
#   bash download_weights.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODELS_DIR="${SCRIPT_DIR}/submodules/MuseTalk/models"

echo "==> モデル保存先: ${MODELS_DIR}"

# ディレクトリ作成
mkdir -p \
  "${MODELS_DIR}/musetalkV15" \
  "${MODELS_DIR}/sd-vae" \
  "${MODELS_DIR}/whisper" \
  "${MODELS_DIR}/dwpose" \
  "${MODELS_DIR}/face-parse-bisent"

# --- HuggingFace Hub ---

# MuseTalk V1.5
echo "==> MuseTalk V1.5 weights"
huggingface-cli download TMElyralab/MuseTalk \
  --local-dir "${MODELS_DIR}" \
  --include "musetalkV15/musetalk.json" "musetalkV15/unet.pth"

# Stable Diffusion VAE
echo "==> SD VAE weights"
huggingface-cli download stabilityai/sd-vae-ft-mse \
  --local-dir "${MODELS_DIR}/sd-vae" \
  --include "config.json" "diffusion_pytorch_model.bin"

# Whisper (Audio Encoder)
echo "==> Whisper weights"
huggingface-cli download openai/whisper-tiny \
  --local-dir "${MODELS_DIR}/whisper" \
  --include "config.json" "pytorch_model.bin" "preprocessor_config.json"

# DWPose
echo "==> DWPose weights"
huggingface-cli download yzd-v/DWPose \
  --local-dir "${MODELS_DIR}/dwpose" \
  --include "dw-ll_ucoco_384.pth"

# --- Google Drive / PyTorch Hub ---

# Face Parse BiSeNet
FACE_PARSE_DIR="${MODELS_DIR}/face-parse-bisent"

if [ ! -f "${FACE_PARSE_DIR}/79999_iter.pth" ]; then
  echo "==> Face Parse BiSeNet weights (Google Drive)"
  gdown --id 154JgKpzCPW82qINcVieuPH3fZ2e0P812 \
    -O "${FACE_PARSE_DIR}/79999_iter.pth"
else
  echo "==> Face Parse BiSeNet weights: already exists, skipping"
fi

if [ ! -f "${FACE_PARSE_DIR}/resnet18-5c106cde.pth" ]; then
  echo "==> ResNet18 weights (PyTorch Hub)"
  curl -L https://download.pytorch.org/models/resnet18-5c106cde.pth \
    -o "${FACE_PARSE_DIR}/resnet18-5c106cde.pth"
else
  echo "==> ResNet18 weights: already exists, skipping"
fi

echo ""
echo "All weights have been downloaded successfully!"
echo "Models directory: ${MODELS_DIR}"
