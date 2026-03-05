from unittest.mock import patch

import pytest

import app.core.dependencies as deps
from app.llm.mock import MockLLMProvider
from app.services.chat_server import ChatServe


class TestGetLlmProvider:
    def test_raises_when_not_initialized(self) -> None:
        original = deps._llm_provider
        try:
            deps._llm_provider = None
            with pytest.raises(RuntimeError, match="初期化されていません"):
                deps.get_llm_provider()
        finally:
            deps._llm_provider = original

    def test_returns_provider_when_initialized(self) -> None:
        original = deps._llm_provider
        try:
            mock_provider = MockLLMProvider(model_name="mock", stream_delay=0.0)
            deps._llm_provider = mock_provider
            assert deps.get_llm_provider() is mock_provider
        finally:
            deps._llm_provider = original


class TestInitializeLlmProvider:
    def test_initializes_with_mock(self) -> None:
        original = deps._llm_provider
        try:
            deps._llm_provider = None
            with patch.dict(
                "os.environ",
                {"APP_NAME": "test", "LLM_MODEL_NAME": "mock", "SERVER_HOST": "0.0.0.0", "SERVER_PORT": "8000", "CORS_ORIGINS": '["*"]'},
                clear=False,
            ):
                from app.core.config import get_settings

                get_settings.cache_clear()
                deps.initialize_llm_provider()
                assert deps._llm_provider is not None
                assert isinstance(deps._llm_provider, MockLLMProvider)
                get_settings.cache_clear()
        finally:
            deps._llm_provider = original


class TestGetChatService:
    def test_returns_chat_serve_instance(self) -> None:
        original = deps._llm_provider
        try:
            deps._llm_provider = MockLLMProvider(
                model_name="mock", stream_delay=0.0
            )
            service = deps.get_chat_service()
            assert isinstance(service, ChatServe)
        finally:
            deps._llm_provider = original
