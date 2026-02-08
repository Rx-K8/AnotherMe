# AnotherMe - AI Avatar Platform

[![TTS Server Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Rx-K8/ac2cfc2237210a437cb17a73d5d4c2a3/raw/tts-server-coverage.json)](https://github.com/Rx-K8/AnotherMe/actions/workflows/test-tts-server.yml)

A monorepo containing the full AnotherMe platform: Frontend, Chat Server, and TTS Server.

## Project Structure

```
AnotherMeProject/
├── frontend/        # React/TypeScript web application
├── chat-server/     # FastAPI chat server with LLM
├── tts-server/      # FastAPI TTS server with Qwen3-TTS
├── scripts/         # Development and build scripts
├── docs/            # Documentation
└── .github/         # CI/CD workflows
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+ (for TTS Server) / 3.13 (for Chat Server)
- uv (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- NVIDIA GPU with CUDA support (for inference)

### Setup

```bash
# One-command setup
./scripts/setup.sh
```

### Running Services

#### Frontend
```bash
cd frontend
npm run dev
```
Access at: http://localhost:5173

#### Chat Server
```bash
cd chat-server
uv run uvicorn app.main:app --reload --port 8000
```
API docs at: http://localhost:8000/docs

#### TTS Server
```bash
cd tts-server
uv run uvicorn app.main:app --reload --port 8001
```
API docs at: http://localhost:8001/docs

## Development

### Linting

```bash
# Lint all projects
./scripts/lint-all.sh

# Format all projects
./scripts/format-all.sh
```

### Testing

```bash
# Run all tests
./scripts/test-all.sh
```

### Pre-commit Hooks

Pre-commit hooks are automatically installed during setup. They will:
- Check file sizes, YAML, TOML, JSON
- Run Ruff (lint + format) on Python code
- Run Biome check on TypeScript code

## Tech Stack

### Frontend
- React 19 + TypeScript
- Vite
- TanStack Router
- Tailwind CSS
- Biome (linting/formatting)

### Chat Server
- Python 3.13
- FastAPI
- PyTorch 2.9.0 (CUDA 12.8)
- Transformers (Gemma-3, Qwen3)
- uv package manager

### TTS Server
- Python 3.12
- FastAPI
- Qwen3-TTS
- PyTorch (CUDA 12.4)
- uv package manager

## Documentation

- [frontend/README.md](frontend/README.md) - Frontend documentation
- [chat-server/README.md](chat-server/README.md) - Chat Server documentation
- [tts-server/README.md](tts-server/README.md) - TTS Server documentation
- [chat-server/DEVELPMENT.md](chat-server/DEVELPMENT.md) - Development guide
- [tts-server/DEVELPMENT.md](tts-server/DEVELPMENT.md) - Development guide

## License

[Your License Here]
