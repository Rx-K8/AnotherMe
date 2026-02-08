from app.schemas.llm import LLMResponse, LLMStreamChunk


class TestLLMResponse:
    def test_create_response(self) -> None:
        response = LLMResponse(
            content="テスト返答",
            finish_reason="stop",
            model="mock-model",
        )
        assert response.content == "テスト返答"
        assert response.finish_reason == "stop"
        assert response.model == "mock-model"

    def test_length_finish_reason(self) -> None:
        response = LLMResponse(
            content="途中まで",
            finish_reason="length",
            model="mock-model",
        )
        assert response.finish_reason == "length"


class TestLLMStreamChunk:
    def test_create_non_final_chunk(self) -> None:
        chunk = LLMStreamChunk(
            content="テ",
            finish_reason="",
            is_final=False,
            model="mock-model",
        )
        assert chunk.content == "テ"
        assert chunk.is_final is False
        assert chunk.finish_reason == ""

    def test_create_final_chunk(self) -> None:
        chunk = LLMStreamChunk(
            content="。",
            finish_reason="stop",
            is_final=True,
            model="mock-model",
        )
        assert chunk.is_final is True
        assert chunk.finish_reason == "stop"
