from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.main import api_router
from app.core.dependencies import get_chat_service
from app.llm.mock import MockLLMProvider
from app.services.chat_server import ChatServe


@pytest.fixture
def mock_llm_provider() -> MockLLMProvider:
    """MockLLMProviderインスタンス（GPU回避）"""
    return MockLLMProvider(model_name="mock", stream_delay=0.0)


@pytest.fixture
def chat_service(mock_llm_provider: MockLLMProvider) -> ChatServe:
    """MockLLMProviderを使用したChatServeインスタンス"""
    return ChatServe(llm_provider=mock_llm_provider)


@pytest.fixture
def app(chat_service: ChatServe) -> FastAPI:
    """テスト用FastAPIアプリケーション（lifespanなし）"""
    test_app = FastAPI(title="Test App")
    test_app.include_router(api_router, prefix="/api")
    test_app.dependency_overrides[get_chat_service] = lambda: chat_service
    return test_app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """非同期HTTPクライアント"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
