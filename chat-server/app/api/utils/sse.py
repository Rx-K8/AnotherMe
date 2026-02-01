"""SSE（Server-Sent Events）ユーティリティモジュール。"""

from collections.abc import AsyncIterator

from pydantic import BaseModel


async def stream_as_sse(
    chunks: AsyncIterator[BaseModel],
) -> AsyncIterator[str]:
    """PydanticモデルのストリームをSSE形式に変換する。

    Args:
        chunks: Pydanticモデルの非同期イテレータ

    Yields:
        SSE形式の文字列
    """
    async for chunk in chunks:
        yield f"data: {chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"
