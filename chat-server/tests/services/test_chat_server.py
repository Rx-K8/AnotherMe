from app.schemas.chat import (
    ChatCompletionChunkResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    Message,
)
from app.services.chat_server import ChatServe


class TestGenerateResponse:
    async def test_returns_chat_completion_response(
        self, chat_service: ChatServe
    ) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")]
        )
        result = await chat_service.generate_response(request)
        assert isinstance(result, ChatCompletionResponse)

    async def test_id_has_prefix(self, chat_service: ChatServe) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")]
        )
        result = await chat_service.generate_response(request)
        assert result.id.startswith("chatcmp-")

    async def test_assistant_role_in_choices(self, chat_service: ChatServe) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")]
        )
        result = await chat_service.generate_response(request)
        assert result.choices[0].message.role == "assistant"

    async def test_content_is_not_empty(self, chat_service: ChatServe) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")]
        )
        result = await chat_service.generate_response(request)
        assert len(result.choices[0].message.content) > 0


class TestGenerateResponseStream:
    async def test_yields_chunk_responses(self, chat_service: ChatServe) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")],
            stream=True,
        )
        chunks = [chunk async for chunk in chat_service.generate_response_stream(request)]
        assert len(chunks) > 0
        assert all(isinstance(c, ChatCompletionChunkResponse) for c in chunks)

    async def test_all_chunks_have_same_id(self, chat_service: ChatServe) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")],
            stream=True,
        )
        chunks = [chunk async for chunk in chat_service.generate_response_stream(request)]
        ids = {c.id for c in chunks}
        assert len(ids) == 1

    async def test_last_chunk_has_stop_finish_reason(
        self, chat_service: ChatServe
    ) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")],
            stream=True,
        )
        chunks = [chunk async for chunk in chat_service.generate_response_stream(request)]
        assert chunks[-1].choices[0].finish_reason == "stop"

    async def test_chunk_id_has_prefix(self, chat_service: ChatServe) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")],
            stream=True,
        )
        chunks = [chunk async for chunk in chat_service.generate_response_stream(request)]
        assert chunks[0].id.startswith("chatcmpl-")
