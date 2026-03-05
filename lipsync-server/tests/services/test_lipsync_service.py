import asyncio
import base64

import pytest
from app.lipsync.mock import _DUMMY_MP4, MockLipsyncProvider
from app.services.lipsync_service import LipsyncService, LipsyncServiceResult


class TestLipsyncService:
    @pytest.fixture
    def service(self) -> LipsyncService:
        return LipsyncService(provider=MockLipsyncProvider())

    @pytest.mark.unit
    async def test_generate_returns_service_result(
        self, service: LipsyncService
    ) -> None:
        result = await service.generate(
            audio_bytes=b"fake audio",
            audio_ext=".wav",
            video_bytes=b"fake video",
            video_ext=".mp4",
        )
        assert isinstance(result, LipsyncServiceResult)

    @pytest.mark.unit
    async def test_generate_returns_valid_base64(self, service: LipsyncService) -> None:
        result = await service.generate(
            audio_bytes=b"fake audio",
            audio_ext=".wav",
            video_bytes=b"fake video",
            video_ext=".mp4",
        )
        decoded = base64.b64decode(result.video_base64)
        assert decoded == _DUMMY_MP4

    @pytest.mark.unit
    async def test_generate_reports_positive_processing_time(
        self, service: LipsyncService
    ) -> None:
        result = await service.generate(
            audio_bytes=b"fake audio",
            audio_ext=".wav",
            video_bytes=b"fake video",
            video_ext=".mp4",
        )
        assert result.processing_time_ms >= 0

    @pytest.mark.unit
    async def test_generate_reports_duration(self, service: LipsyncService) -> None:
        result = await service.generate(
            audio_bytes=b"fake audio",
            audio_ext=".wav",
            video_bytes=b"fake video",
            video_ext=".mp4",
        )
        assert result.duration_seconds > 0

    @pytest.mark.unit
    async def test_generate_passes_parameters_to_provider(self) -> None:
        """パラメータがproviderに正しく渡されることを確認"""
        captured: dict[str, object] = {}

        class CapturingProvider(MockLipsyncProvider):
            async def generate(
                self,
                audio_path: str,
                video_path: str,
                bbox_shift: int = 0,
                extra_margin: int = 10,
                parsing_mode: str = "jaw",
            ) -> "LipsyncServiceResult":  # type: ignore[override]
                captured["bbox_shift"] = bbox_shift
                captured["extra_margin"] = extra_margin
                captured["parsing_mode"] = parsing_mode
                return await super().generate(
                    audio_path, video_path, bbox_shift, extra_margin, parsing_mode
                )

        service = LipsyncService(provider=CapturingProvider())
        await service.generate(
            audio_bytes=b"audio",
            audio_ext=".wav",
            video_bytes=b"video",
            video_ext=".mp4",
            bbox_shift=5,
            extra_margin=20,
            parsing_mode="face",
        )
        assert captured["bbox_shift"] == 5
        assert captured["extra_margin"] == 20
        assert captured["parsing_mode"] == "face"

    @pytest.mark.unit
    async def test_semaphore_limits_concurrency(self, service: LipsyncService) -> None:
        """セマフォにより同時実行が1に制限されることを確認"""
        running = 0
        max_running = 0

        original_generate = service._provider.generate

        async def slow_generate(**kwargs: object) -> object:
            nonlocal running, max_running
            running += 1
            max_running = max(max_running, running)
            await asyncio.sleep(0.05)
            result = await original_generate(
                audio_path=str(kwargs.get("audio_path", "/tmp/a.wav")),
                video_path=str(kwargs.get("video_path", "/tmp/a.mp4")),
            )
            running -= 1
            return result

        service._provider.generate = slow_generate  # type: ignore[assignment]

        tasks = [
            service.generate(
                audio_bytes=b"audio",
                audio_ext=".wav",
                video_bytes=b"video",
                video_ext=".mp4",
            )
            for _ in range(3)
        ]
        await asyncio.gather(*tasks)
        assert max_running == 1

    @pytest.mark.unit
    async def test_tempfiles_cleaned_up_after_generate(
        self, service: LipsyncService
    ) -> None:
        """一時ファイルが生成後に削除されることを確認"""
        import glob
        import tempfile

        temp_dir = tempfile.gettempdir()
        # 生成前のtmpファイル数を記録
        before = set(glob.glob(f"{temp_dir}/lipsync_*"))

        await service.generate(
            audio_bytes=b"fake audio",
            audio_ext=".wav",
            video_bytes=b"fake video",
            video_ext=".mp4",
        )

        after = set(glob.glob(f"{temp_dir}/lipsync_*"))
        # 新しい一時ファイルが残っていないこと
        assert after - before == set()

    @pytest.mark.unit
    async def test_tempfiles_cleaned_up_on_provider_error(self) -> None:
        """プロバイダーエラー時も一時ファイルが削除されること"""
        import glob
        import tempfile

        class FailingProvider(MockLipsyncProvider):
            async def generate(self, *args: object, **kwargs: object) -> object:  # type: ignore[override]
                raise RuntimeError("GPU error")

        service = LipsyncService(provider=FailingProvider())
        temp_dir = tempfile.gettempdir()
        before = set(glob.glob(f"{temp_dir}/lipsync_*"))

        with pytest.raises(RuntimeError, match="GPU error"):
            await service.generate(
                audio_bytes=b"audio",
                audio_ext=".wav",
                video_bytes=b"video",
                video_ext=".mp4",
            )

        after = set(glob.glob(f"{temp_dir}/lipsync_*"))
        assert after - before == set()
