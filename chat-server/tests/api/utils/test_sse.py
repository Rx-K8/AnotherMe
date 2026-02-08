import json

from pydantic import BaseModel

from app.api.utils.sse import stream_as_sse


class SampleChunk(BaseModel):
    content: str


class TestStreamAsSse:
    async def test_single_chunk_format(self) -> None:
        async def single_chunk():  # type: ignore[no-untyped-def]
            yield SampleChunk(content="テスト")

        results = [line async for line in stream_as_sse(single_chunk())]
        assert len(results) == 2  # 1チャンク + [DONE]
        parsed = json.loads(results[0].removeprefix("data: ").strip())
        assert parsed["content"] == "テスト"
        assert results[1] == "data: [DONE]\n\n"

    async def test_multiple_chunks(self) -> None:
        async def multi_chunks():  # type: ignore[no-untyped-def]
            yield SampleChunk(content="A")
            yield SampleChunk(content="B")

        results = [line async for line in stream_as_sse(multi_chunks())]
        assert len(results) == 3  # 2チャンク + [DONE]

    async def test_done_always_sent(self) -> None:
        async def empty_stream():  # type: ignore[no-untyped-def]
            return
            yield  # type: ignore[misc]

        results = [line async for line in stream_as_sse(empty_stream())]
        assert len(results) == 1
        assert results[0] == "data: [DONE]\n\n"
