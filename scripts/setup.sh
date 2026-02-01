#!/usr/bin/env bash
set -e

echo "=== AnotherMe Monorepo Setup ==="
echo ""

# Check dependencies
command -v node >/dev/null 2>&1 || { echo "Error: Node.js is required"; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "Error: uv is required. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }

echo "1. Setting up Frontend..."
cd frontend
npm install
cd ..

echo ""
echo "2. Setting up Chat Server..."
cd chat-server
uv python install
uv sync --group dev
cd ..

echo ""
echo "3. Setting up TTS Server..."
cd tts-server
uv python install
uv sync --group dev
cd ..

echo ""
echo "4. Installing pre-commit hooks..."
command -v pre-commit >/dev/null 2>&1 && pre-commit install || echo "pre-commit not found, skipping..."

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  - Frontend:    cd frontend && npm run dev"
echo "  - Chat Server: cd chat-server && uv run uvicorn app.main:app --reload --port 8000"
echo "  - TTS Server:  cd tts-server && uv run uvicorn app.main:app --reload --port 8001"
