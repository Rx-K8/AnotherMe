from app.llm.mock import MockLLMProvider
from app.schemas.chat import Message
from app.schemas.llm import LLMResponse, LLMStreamChunk


class TestMockLLMProviderGenerate:
    async def test_returns_llm_response(
        self, mock_llm_provider: MockLLMProvider
    ) -> None:
        messages = [Message(role="user", content="テスト")]
        result = await mock_llm_provider.generate(messages)
        assert isinstance(result, LLMResponse)

    async def test_finish_reason_is_stop(
        self, mock_llm_provider: MockLLMProvider
    ) -> None:
        messages = [Message(role="user", content="テスト")]
        result = await mock_llm_provider.generate(messages)
        assert result.finish_reason == "stop"

    async def test_response_contains_greeting_and_conclusion(
        self, mock_llm_provider: MockLLMProvider
    ) -> None:
        messages = [Message(role="user", content="テスト")]
        result = await mock_llm_provider.generate(messages)
        # レスポンスは「挨拶\n\n本文\n\n結び」の構造
        parts = result.content.split("\n\n")
        assert len(parts) == 3

    async def test_model_name_in_response(
        self, mock_llm_provider: MockLLMProvider
    ) -> None:
        messages = [Message(role="user", content="テスト")]
        result = await mock_llm_provider.generate(messages)
        assert result.model == "mock"

    async def test_temperature_and_max_tokens_accepted(
        self, mock_llm_provider: MockLLMProvider
    ) -> None:
        messages = [Message(role="user", content="テスト")]
        result = await mock_llm_provider.generate(
            messages, temperature=0.5, max_new_tokens=100
        )
        assert isinstance(result, LLMResponse)


class TestMockLLMProviderGenerateStream:
    async def test_yields_stream_chunks(
        self, mock_llm_provider: MockLLMProvider
    ) -> None:
        messages = [Message(role="user", content="テスト")]
        chunks = [
            chunk async for chunk in mock_llm_provider.generate_stream(messages)
        ]
        assert len(chunks) > 0
        assert all(isinstance(c, LLMStreamChunk) for c in chunks)

    async def test_last_chunk_is_final(
        self, mock_llm_provider: MockLLMProvider
    ) -> None:
        messages = [Message(role="user", content="テスト")]
        chunks = [
            chunk async for chunk in mock_llm_provider.generate_stream(messages)
        ]
        assert chunks[-1].is_final is True
        assert chunks[-1].finish_reason == "stop"

    async def test_non_final_chunks_are_not_final(
        self, mock_llm_provider: MockLLMProvider
    ) -> None:
        messages = [Message(role="user", content="テスト")]
        chunks = [
            chunk async for chunk in mock_llm_provider.generate_stream(messages)
        ]
        for chunk in chunks[:-1]:
            assert chunk.is_final is False


class TestGenerateResponseText:
    def test_with_user_message(self) -> None:
        provider = MockLLMProvider(model_name="mock", stream_delay=0.0)
        result = provider._generate_response_text("テスト")
        assert "テスト" in result

    def test_with_none_message(self) -> None:
        provider = MockLLMProvider(model_name="mock", stream_delay=0.0)
        result = provider._generate_response_text(None)
        assert "何かお手伝いできることはありますか？" in result

    def test_long_message_truncated(self) -> None:
        provider = MockLLMProvider(model_name="mock", stream_delay=0.0)
        long_message = "あ" * 30
        result = provider._generate_response_text(long_message)
        assert "..." in result
