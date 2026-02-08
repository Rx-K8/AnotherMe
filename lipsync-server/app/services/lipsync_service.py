"""リップシンクサービス層"""

import asyncio
import base64
import os
import tempfile
import time
from dataclasses import dataclass

from app.lipsync.abc import LipsyncProvider


@dataclass(frozen=True)
class LipsyncServiceResult:
    """サービス層の処理結果"""

    video_base64: str
    duration_seconds: float
    processing_time_ms: int


class LipsyncService:
    """リップシンク生成サービス

    GPU排他制御、一時ファイル管理、base64変換を担当する。
    """

    def __init__(self, provider: LipsyncProvider) -> None:
        self._provider = provider
        self._semaphore = asyncio.Semaphore(1)

    async def generate(
        self,
        audio_bytes: bytes,
        audio_ext: str,
        video_bytes: bytes,
        video_ext: str,
        bbox_shift: int = 0,
        extra_margin: int = 10,
        parsing_mode: str = "jaw",
    ) -> LipsyncServiceResult:
        audio_path: str | None = None
        video_path: str | None = None

        async with self._semaphore:
            try:
                start = time.monotonic()

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=audio_ext, prefix="lipsync_audio_"
                ) as af:
                    af.write(audio_bytes)
                    audio_path = af.name

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=video_ext, prefix="lipsync_video_"
                ) as vf:
                    vf.write(video_bytes)
                    video_path = vf.name

                result = await self._provider.generate(
                    audio_path=audio_path,
                    video_path=video_path,
                    bbox_shift=bbox_shift,
                    extra_margin=extra_margin,
                    parsing_mode=parsing_mode,
                )

                elapsed_ms = int((time.monotonic() - start) * 1000)
                video_base64 = base64.b64encode(result.video_bytes).decode("utf-8")

                return LipsyncServiceResult(
                    video_base64=video_base64,
                    duration_seconds=result.duration_seconds,
                    processing_time_ms=elapsed_ms,
                )
            finally:
                if audio_path is not None:
                    os.unlink(audio_path)
                if video_path is not None:
                    os.unlink(video_path)
