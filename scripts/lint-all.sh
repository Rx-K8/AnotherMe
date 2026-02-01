#!/usr/bin/env bash
set -e

echo "=== Linting All Projects ==="

echo ""
echo "1. Linting Chat Server..."
cd chat-server
./scripts/lint.sh
cd ..

echo ""
echo "2. Linting TTS Server..."
cd tts-server
./scripts/lint.sh
cd ..

echo ""
echo "3. Linting Frontend..."
cd frontend
npm run lint
cd ..

echo ""
echo "✓ All linting complete!"
