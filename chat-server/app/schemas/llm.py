from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """LLMプロバイダーからのレスポンス。"""

    content: str = Field(..., description="モデルから生成されたテキスト内容。")
    finish_reason: str = Field(
        ...,
        description="モデルがトークン生成を停止した理由（例: 'stop', 'length'）。",
    )
    model: str = Field(..., description="完了に使用されたモデル。")


class LLMStreamChunk(BaseModel):
    """ストリーミングレスポンスのLLMプロバイダーからのチャンク。"""

    content: str = Field(
        ..., description="ストリーミングレスポンスからのこのチャンクの内容。"
    )
    finish_reason: str = Field(
        ...,
        description="停止理由。最後のチャンクでない場合は空文字列。",
    )
    is_final: bool = Field(
        ..., description="これがストリーミングレスポンスの最後のチャンクかどうか。"
    )
    model: str = Field(..., description="チャンクに使用されたモデル。")
