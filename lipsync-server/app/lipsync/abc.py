"""リップシンクプロバイダーの抽象基底クラス"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LipsyncResult:
    """リップシンク生成結果"""

    video_bytes: bytes
    duration_seconds: float


class LipsyncProvider(ABC):
    """リップシンクプロバイダーの抽象基底クラス

    全てのリップシンクプロバイダー（MuseTalk等）は
    このクラスを継承して実装する。
    """

    @abstractmethod
    async def generate(
        self,
        audio_path: str,
        video_path: str,
        bbox_shift: int = 0,
        extra_margin: int = 10,
        parsing_mode: str = "jaw",
    ) -> LipsyncResult:
        """音声と動画/画像からリップシンク動画を生成する

        Args:
            audio_path: 音声ファイルのパス
            video_path: 動画/画像ファイルのパス
            bbox_shift: バウンディングボックスのシフト量
            extra_margin: 顔領域の追加マージン
            parsing_mode: 顔パースモード ("jaw" or "face")

        Returns:
            LipsyncResult: 生成された動画データ
        """
        pass

    @abstractmethod
    async def is_ready(self) -> bool:
        """プロバイダーが使用可能な状態かどうかを返す"""
        pass
