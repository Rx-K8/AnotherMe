import time
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """チャット会話内のメッセージ。"""

    role: Literal["user", "assistant", "system"] = Field(
        ..., description="このメッセージの作成者のロール。"
    )
    content: str = Field(..., description="メッセージの内容。")

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        """コンテンツが空でないことを検証する。"""
        if not v.strip():
            raise ValueError("メッセージの内容は空にできません。")
        return v

    def to_dict(self) -> dict[str, str]:
        """メッセージを辞書形式に変換する。"""
        return {"role": self.role, "content": self.content}


class ChatCompletionRequest(BaseModel):
    """チャット完了作成のリクエストボディ。"""

    messages: list[Message] = Field(
        ...,
        description="これまでの会話を構成するメッセージのリスト。",
        min_length=1,
    )
    stream: bool = Field(
        default=False,
        description="設定すると、部分的なメッセージデルタがSSEで送信される。",
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="サンプリング温度（0.0-1.0）。高いほどランダム性が増す。",
    )
    max_new_tokens: int | None = Field(
        default=None,
        gt=0,
        description="生成する最大トークン数。",
    )

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: list[Message]) -> list[Message]:
        """メッセージリストのバリデーション。"""
        if not v:
            raise ValueError("メッセージリストは空にできません。")
        return v


class Choice(BaseModel):
    """モデルが生成したチャット完了の選択肢。"""

    index: int = Field(..., description="選択肢リスト内のこの選択肢のインデックス。")
    message: Message = Field(
        ..., description="モデルが生成したチャット完了メッセージ。"
    )
    finish_reason: str | None = Field(
        default="stop",
        description=(
            "モデルがトークン生成を停止した理由。"
            "自然な停止点または指定された停止シーケンスの場合は'stop'、"
            "最大トークン数に達した場合は'length'、"
            "コンテンツフィルターにより省略された場合は'content_filter'。"
        ),
    )


class ChatCompletionResponse(BaseModel):
    """モデルが返すチャット完了レスポンス。"""

    id: str = Field(..., description="チャット完了の一意な識別子。")
    object: str = Field(
        default="chat.completion",
        description="オブジェクトタイプ。常に'chat.completion'。",
    )
    created: int = Field(
        default_factory=lambda: int(time.time()),
        description="チャット完了が作成されたUnixタイムスタンプ（秒）。",
    )
    choices: list[Choice] = Field(
        ...,
        description="チャット完了の選択肢リスト。nが1より大きい場合、複数になる。",
    )


class Delta(BaseModel):
    """ストリーミングモデルレスポンスで生成されたチャット完了デルタ。"""

    role: Literal["assistant"] | None = Field(
        default=None, description="このメッセージの作成者のロール。"
    )
    content: str | None = Field(
        default=None,
        description=(
            "チャンクメッセージの内容。"
            "最初のチャンクでは空で、後続のチャンクで値が入る。"
        ),
    )


class ChoiceChunk(BaseModel):
    """ストリーミング中に生成されたチャット完了の選択肢チャンク。"""

    index: int = Field(..., description="選択肢リスト内のこの選択肢のインデックス。")
    delta: Delta = Field(
        ...,
        description="ストリーミングモデルレスポンスで生成されたチャット完了デルタ。",
    )
    finish_reason: str | None = Field(
        default=None,
        description=(
            "モデルがトークン生成を停止した理由。最後のチャンク以外ではnull。"
        ),
    )


class ChatCompletionChunkResponse(BaseModel):
    """ストリーミングされたチャット完了レスポンスのチャンク。"""

    id: str = Field(..., description="チャット完了チャンクの一意な識別子。")
    object: str = Field(
        default="chat.completion.chunk",
        description="オブジェクトタイプ。常に'chat.completion.chunk'。",
    )
    created: int = Field(
        default_factory=lambda: int(time.time()),
        description="チャット完了チャンクが作成されたUnixタイムスタンプ（秒）。",
    )
    choices: list[ChoiceChunk] = Field(
        ...,
        description="チャット完了の選択肢リスト。nが1より大きい場合、複数になる。",
    )
