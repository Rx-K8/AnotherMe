#!/usr/bin/env bash
set -e

echo "=== Running All Tests ==="

echo ""
echo "1. Testing TTS Server..."
cd tts-server
uv run pytest tests/ -v
cd ..

# Add other test commands as they become available
# echo ""
# echo "2. Testing Chat Server..."
# cd chat-server
# uv run pytest tests/ -v
# cd ..

echo ""
echo "✓ All tests complete!"
