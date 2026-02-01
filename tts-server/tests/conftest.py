from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.main import api_router


@pytest.fixture
def mock_tts_provider() -> MagicMock:
    """Qwen3TTSProviderのモック（GPU回避）"""
    mock = MagicMock()
    mock.synthesize_with_reference = AsyncMock(
        return_value=b"RIFF$\x00\x00\x00WAVEfmt "
    )
    return mock


@pytest.fixture
def app(mock_tts_provider: MagicMock) -> FastAPI:
    """テスト用FastAPIアプリケーション"""
    test_app = FastAPI(title="Test App")
    test_app.include_router(api_router)
    test_app.state.tts_provider = mock_tts_provider
    return test_app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """非同期HTTPクライアント"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_wav_content() -> bytes:
    """テスト用WAVファイル（最小限の有効なヘッダー）"""
    return (
        b"RIFF"
        b"\x24\x00\x00\x00"
        b"WAVE"
        b"fmt "
        b"\x10\x00\x00\x00"
        b"\x01\x00"
        b"\x01\x00"
        b"\x44\xac\x00\x00"
        b"\x88\x58\x01\x00"
        b"\x02\x00"
        b"\x10\x00"
        b"data"
        b"\x00\x00\x00\x00"
    )


@pytest.fixture
def large_file_content() -> bytes:
    """10MBを超えるテスト用コンテンツ"""
    return b"x" * (10 * 1024 * 1024 + 1)
