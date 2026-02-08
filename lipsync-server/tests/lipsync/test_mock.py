import pytest
from app.lipsync.abc import LipsyncResult
from app.lipsync.mock import MockLipsyncProvider


class TestMockLipsyncProvider:
    @pytest.fixture
    def provider(self) -> MockLipsyncProvider:
        return MockLipsyncProvider()

    @pytest.mark.unit
    async def test_generate_returns_lipsync_result(
        self, provider: MockLipsyncProvider
    ) -> None:
        result = await provider.generate(
            audio_path="/tmp/test.wav",
            video_path="/tmp/test.mp4",
        )
        assert isinstance(result, LipsyncResult)
        assert isinstance(result.video_bytes, bytes)
        assert len(result.video_bytes) > 0
        assert result.duration_seconds > 0

    @pytest.mark.unit
    async def test_is_ready_returns_true(self, provider: MockLipsyncProvider) -> None:
        assert await provider.is_ready() is True

    @pytest.mark.unit
    async def test_generate_accepts_all_parameters(
        self, provider: MockLipsyncProvider
    ) -> None:
        result = await provider.generate(
            audio_path="/tmp/test.wav",
            video_path="/tmp/test.mp4",
            bbox_shift=5,
            extra_margin=20,
            parsing_mode="face",
        )
        assert isinstance(result, LipsyncResult)

    @pytest.mark.unit
    async def test_generate_returns_consistent_results(
        self, provider: MockLipsyncProvider
    ) -> None:
        result1 = await provider.generate(
            audio_path="/tmp/a.wav", video_path="/tmp/a.mp4"
        )
        result2 = await provider.generate(
            audio_path="/tmp/b.wav", video_path="/tmp/b.mp4"
        )
        assert result1.video_bytes == result2.video_bytes
        assert result1.duration_seconds == result2.duration_seconds
