"""テスト・開発用のモックリップシンクプロバイダー"""

from app.lipsync.abc import LipsyncProvider, LipsyncResult

# 最小限のダミーMP4バイト列（ftyp box header）
_DUMMY_MP4 = b"\x00\x00\x00\x1c\x66\x74\x79\x70\x69\x73\x6f\x6d"

_DUMMY_DURATION = 1.0


class MockLipsyncProvider(LipsyncProvider):
    """GPU不要のモックプロバイダー。固定ダミーMP4データを返す。"""

    async def generate(
        self,
        audio_path: str,
        video_path: str,
        bbox_shift: int = 0,
        extra_margin: int = 10,
        parsing_mode: str = "jaw",
    ) -> LipsyncResult:
        return LipsyncResult(
            video_bytes=_DUMMY_MP4,
            duration_seconds=_DUMMY_DURATION,
        )

    async def is_ready(self) -> bool:
        return True
