import uuid
from collections.abc import AsyncIterator

from app.llm.abc import LLMProvider
from app.schemas.chat import (
    ChatCompletionChunkResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ChoiceChunk,
    Delta,
    Message,
)


class ChatServe:
    """
    チャット機能を提供するサービスクラス

    LLM Providerを使用してチャット応答を生成する
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def generate_response(
        self,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        """
        チャット応答を生成する

        Args:
            request: チャット完了リクエスト

        Returns:
            ChatCompletionResponse: 生成されたチャット応答
        """
        llm_response = await self.llm_provider.generate(
            messages=request.messages,
            temperature=request.temperature,
            max_new_tokens=request.max_new_tokens,
        )

        choices = [
            Choice(
                index=0,
                message=Message(role="assistant", content=llm_response.content),
                finish_reason=llm_response.finish_reason,
            )
        ]

        return ChatCompletionResponse(id=f"chatcmp-{uuid.uuid4()}", choices=choices)

    async def generate_response_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunkResponse]:
        """
        ストリーミング形式でチャット応答を生成する

        Args:
            request: チャット完了リクエスト

        Yields:
            ChatCompletionChunkResponse: ストリーミング応答のチャンク
        """
        response_id = f"chatcmpl-{uuid.uuid4()}"

        async for chunk in self.llm_provider.generate_stream(
            messages=request.messages,
            temperature=request.temperature,
            max_new_tokens=request.max_new_tokens,
        ):
            choice_chunk = ChoiceChunk(
                index=0,
                delta=Delta(
                    role="assistant" if chunk.is_final is False else None,
                    content=chunk.content,
                ),
                finish_reason=chunk.finish_reason if chunk.is_final else None,
            )

            yield ChatCompletionChunkResponse(
                id=response_id,
                choices=[choice_chunk],
            )
