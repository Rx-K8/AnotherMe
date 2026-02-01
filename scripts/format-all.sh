#!/usr/bin/env bash
set -e

echo "=== Formatting All Projects ==="

echo ""
echo "1. Formatting Chat Server..."
cd chat-server
./scripts/format.sh
cd ..

echo ""
echo "2. Formatting TTS Server..."
cd tts-server
./scripts/format.sh
cd ..

echo ""
echo "3. Formatting Frontend..."
cd frontend
npm run format
cd ..

echo ""
echo "✓ All formatting complete!"
