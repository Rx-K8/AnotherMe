"""APIリクエスト・レスポンスのスキーマ定義"""

from pydantic import BaseModel, Field


class TTSResponse(BaseModel):
    """音声合成APIのレスポンス定義"""

    audio_data: str = Field(..., description="Base64エンコードされた音声データ")


class TTSErrorResponse(BaseModel):
    """音声合成APIのエラーレスポンス定義"""

    error: str = Field(..., description="エラーメッセージ")
    detail: str | None = Field(default=None, description="詳細なエラー情報")
