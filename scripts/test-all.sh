#!/usr/bin/env bash
set -e

echo "=== Running All Tests ==="

# --ci フラグで CPU 版 PyTorch を使用
UV_EXTRA=""
if [ "$1" = "--ci" ]; then
    UV_EXTRA="--extra cpu"
fi

echo ""
echo "1. Testing TTS Server..."
cd tts-server
uv run $UV_EXTRA pytest tests/ -v
cd ..

# Add other test commands as they become available
# echo ""
# echo "2. Testing Chat Server..."
# cd chat-server
# uv run $UV_EXTRA pytest tests/ -v
# cd ..

echo ""
echo "✓ All tests complete!"
