import pytest
from pydantic import ValidationError

from app.schemas.chat import (
    ChatCompletionChunkResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ChoiceChunk,
    Delta,
    Message,
)


class TestMessage:
    def test_create_user_message(self) -> None:
        msg = Message(role="user", content="こんにちは")
        assert msg.role == "user"
        assert msg.content == "こんにちは"

    def test_create_assistant_message(self) -> None:
        msg = Message(role="assistant", content="お元気ですか？")
        assert msg.role == "assistant"

    def test_create_system_message(self) -> None:
        msg = Message(role="system", content="あなたはAIアシスタントです。")
        assert msg.role == "system"

    def test_reject_invalid_role(self) -> None:
        with pytest.raises(ValidationError):
            Message(role="invalid", content="テスト")  # type: ignore[arg-type]

    def test_reject_empty_content(self) -> None:
        with pytest.raises(ValidationError, match="空にできません"):
            Message(role="user", content="")

    def test_reject_whitespace_only_content(self) -> None:
        with pytest.raises(ValidationError, match="空にできません"):
            Message(role="user", content="   ")

    def test_to_dict(self) -> None:
        msg = Message(role="user", content="テスト")
        result = msg.to_dict()
        assert result == {"role": "user", "content": "テスト"}


class TestChatCompletionRequest:
    def test_create_minimal_request(self) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")]
        )
        assert len(request.messages) == 1
        assert request.stream is False
        assert request.temperature is None
        assert request.max_new_tokens is None

    def test_create_full_request(self) -> None:
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="テスト")],
            stream=True,
            temperature=0.7,
            max_new_tokens=100,
        )
        assert request.stream is True
        assert request.temperature == 0.7
        assert request.max_new_tokens == 100

    def test_reject_empty_messages(self) -> None:
        with pytest.raises(ValidationError):
            ChatCompletionRequest(messages=[])

    def test_reject_temperature_above_range(self) -> None:
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                messages=[Message(role="user", content="テスト")],
                temperature=1.1,
            )

    def test_reject_temperature_below_range(self) -> None:
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                messages=[Message(role="user", content="テスト")],
                temperature=-0.1,
            )

    def test_reject_max_new_tokens_zero(self) -> None:
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                messages=[Message(role="user", content="テスト")],
                max_new_tokens=0,
            )

    def test_reject_max_new_tokens_negative(self) -> None:
        with pytest.raises(ValidationError):
            ChatCompletionRequest(
                messages=[Message(role="user", content="テスト")],
                max_new_tokens=-1,
            )


class TestChatCompletionResponse:
    def test_default_values(self) -> None:
        response = ChatCompletionResponse(
            id="chatcmp-test",
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content="返答"),
                )
            ],
        )
        assert response.object == "chat.completion"
        assert isinstance(response.created, int)
        assert response.created > 0

    def test_choices_structure(self) -> None:
        response = ChatCompletionResponse(
            id="chatcmp-test",
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content="返答"),
                    finish_reason="stop",
                )
            ],
        )
        assert len(response.choices) == 1
        assert response.choices[0].finish_reason == "stop"


class TestChatCompletionChunkResponse:
    def test_default_values(self) -> None:
        chunk = ChatCompletionChunkResponse(
            id="chatcmpl-test",
            choices=[
                ChoiceChunk(
                    index=0,
                    delta=Delta(role="assistant", content="テ"),
                )
            ],
        )
        assert chunk.object == "chat.completion.chunk"
        assert isinstance(chunk.created, int)

    def test_delta_with_content_only(self) -> None:
        delta = Delta(content="テスト")
        assert delta.role is None
        assert delta.content == "テスト"

    def test_choice_chunk_finish_reason(self) -> None:
        chunk = ChoiceChunk(
            index=0,
            delta=Delta(content=""),
            finish_reason="stop",
        )
        assert chunk.finish_reason == "stop"
