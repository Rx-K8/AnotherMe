"""APIリクエスト・レスポンスのスキーマ定義"""

from enum import Enum

from pydantic import BaseModel, Field


class ParsingMode(str, Enum):
    """顔パースモード"""

    JAW = "jaw"
    FACE = "face"


class LipsyncResponse(BaseModel):
    """リップシンク生成APIのレスポンス定義"""

    video_data: str = Field(..., description="Base64エンコードされたMP4動画データ")
    duration_seconds: float = Field(..., description="生成動画の長さ（秒）")
    processing_time_ms: int = Field(..., description="処理時間（ミリ秒）")


class LipsyncErrorResponse(BaseModel):
    """リップシンク生成APIのエラーレスポンス定義"""

    error: str = Field(..., description="エラーメッセージ")
    detail: str | None = Field(default=None, description="詳細なエラー情報")
