from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.utils.sse import stream_as_sse
from app.core.dependencies import get_chat_service
from app.schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from app.services.chat_server import ChatServe

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/completions",
    response_model=ChatCompletionResponse,
    summary="チャットエンドポイント",
    description="チャット応答を取得します",
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    chat_service: ChatServe = Depends(get_chat_service),
) -> ChatCompletionResponse | StreamingResponse:
    """
    チャット完了エンドポイント

    Args:
        request: チャット完了リクエスト
        chat_service: チャットサービス（依存性注入）

    Returns:
        ChatCompletionResponse | StreamingResponse: 生成されたチャット応答
    """
    if request.stream:
        return StreamingResponse(
            stream_as_sse(chat_service.generate_response_stream(request)),
            media_type="text/event-stream",
        )

    return await chat_service.generate_response(request)
