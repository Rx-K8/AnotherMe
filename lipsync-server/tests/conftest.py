"""共有テストフィクスチャ"""

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.api.main import api_router
from app.services.lipsync_service import LipsyncServiceResult
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def mock_lipsync_service() -> MagicMock:
    """LipsyncServiceのモック"""
    mock = MagicMock()
    mock.generate = AsyncMock(
        return_value=LipsyncServiceResult(
            video_base64="dGVzdA==",
            duration_seconds=1.0,
            processing_time_ms=100,
        )
    )
    return mock


@pytest.fixture
def app(mock_lipsync_service: MagicMock) -> FastAPI:
    """テスト用FastAPIアプリケーション"""
    test_app = FastAPI(title="Test App")
    test_app.include_router(api_router)
    test_app.state.lipsync_service = mock_lipsync_service
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
def sample_mp4_content() -> bytes:
    """テスト用MP4ファイル（最小限のftypヘッダー）"""
    return b"\x00\x00\x00\x1c\x66\x74\x79\x70\x69\x73\x6f\x6d"
