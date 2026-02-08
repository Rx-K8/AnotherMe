from collections.abc import AsyncGenerator

from app.llm.abc import LLMProvider
from app.schemas.chat import Message
from app.schemas.llm import LLMResponse, LLMStreamChunk


class ConcreteLLMProvider(LLMProvider):
    """テスト用の具象LLMProviderサブクラス"""

    def __init__(self, max_new_tokens: int = 1000) -> None:
        self.max_new_tokens = max_new_tokens

    async def generate(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_new_tokens: int | None = None,
    ) -> LLMResponse:
        return LLMResponse(content="test", finish_reason="stop", model="test")

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_new_tokens: int | None = None,
    ) -> AsyncGenerator[LLMStreamChunk]:
        yield LLMStreamChunk(
            content="test", finish_reason="stop", is_final=True, model="test"
        )


class TestGetValidatedMaxNewTokens:
    def test_none_returns_default(self) -> None:
        provider = ConcreteLLMProvider(max_new_tokens=1000)
        assert provider._get_validated_max_new_tokens(None) == 1000

    def test_smaller_value_returns_as_is(self) -> None:
        provider = ConcreteLLMProvider(max_new_tokens=1000)
        assert provider._get_validated_max_new_tokens(100) == 100

    def test_larger_value_returns_default(self) -> None:
        provider = ConcreteLLMProvider(max_new_tokens=1000)
        assert provider._get_validated_max_new_tokens(9999) == 1000

    def test_equal_value_returns_as_is(self) -> None:
        provider = ConcreteLLMProvider(max_new_tokens=1000)
        assert provider._get_validated_max_new_tokens(1000) == 1000
