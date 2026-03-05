"""リップシンク生成APIのテスト"""

from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient


class TestGenerateLipsync:
    """POST /api/lipsync/generate のテスト"""

    async def test_generate_success_with_wav_and_mp4(
        self,
        client: AsyncClient,
        mock_lipsync_service: MagicMock,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "video_data" in data
        assert "duration_seconds" in data
        assert "processing_time_ms" in data
        mock_lipsync_service.generate.assert_called_once()

    async def test_generate_success_with_mp3_and_jpg(
        self,
        client: AsyncClient,
        mock_lipsync_service: MagicMock,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.mp3", sample_wav_content, "audio/mpeg"),
                "video_file": ("test.jpg", sample_mp4_content, "image/jpeg"),
            },
        )
        assert response.status_code == 200
        call_kwargs = mock_lipsync_service.generate.call_args.kwargs
        assert call_kwargs["audio_ext"] == ".mp3"
        assert call_kwargs["video_ext"] == ".jpg"

    async def test_generate_with_custom_parameters(
        self,
        client: AsyncClient,
        mock_lipsync_service: MagicMock,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
            data={
                "bbox_shift": "5",
                "extra_margin": "20",
                "parsing_mode": "face",
            },
        )
        assert response.status_code == 200
        call_kwargs = mock_lipsync_service.generate.call_args.kwargs
        assert call_kwargs["bbox_shift"] == 5
        assert call_kwargs["extra_margin"] == 20
        assert call_kwargs["parsing_mode"] == "face"

    async def test_generate_uses_default_parameters(
        self,
        client: AsyncClient,
        mock_lipsync_service: MagicMock,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
        )
        assert response.status_code == 200
        call_kwargs = mock_lipsync_service.generate.call_args.kwargs
        assert call_kwargs["bbox_shift"] == 0
        assert call_kwargs["extra_margin"] == 10
        assert call_kwargs["parsing_mode"] == "jaw"

    async def test_generate_rejects_unsupported_audio_format(
        self,
        client: AsyncClient,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.ogg", sample_wav_content, "audio/ogg"),
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
        )
        assert response.status_code == 400

    async def test_generate_rejects_unsupported_video_format(
        self,
        client: AsyncClient,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
                "video_file": ("test.avi", sample_mp4_content, "video/avi"),
            },
        )
        assert response.status_code == 400

    async def test_generate_rejects_oversized_audio(
        self,
        client: AsyncClient,
        sample_mp4_content: bytes,
    ) -> None:
        large_audio = b"x" * (10 * 1024 * 1024 + 1)
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", large_audio, "audio/wav"),
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
        )
        assert response.status_code == 400

    async def test_generate_rejects_empty_video_file(
        self,
        client: AsyncClient,
        sample_wav_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
                "video_file": ("test.mp4", b"", "video/mp4"),
            },
        )
        assert response.status_code == 400

    async def test_generate_missing_audio_file(
        self,
        client: AsyncClient,
        sample_mp4_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
        )
        assert response.status_code == 422

    async def test_generate_missing_video_file(
        self,
        client: AsyncClient,
        sample_wav_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
            },
        )
        assert response.status_code == 422

    async def test_generate_invalid_parsing_mode(
        self,
        client: AsyncClient,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
            data={"parsing_mode": "invalid"},
        )
        assert response.status_code == 422

    async def test_generate_value_error_returns_400(
        self,
        client: AsyncClient,
        mock_lipsync_service: MagicMock,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        mock_lipsync_service.generate = AsyncMock(
            side_effect=ValueError("無効なパラメータ")
        )
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
        )
        assert response.status_code == 400

    async def test_generate_runtime_error_returns_500(
        self,
        client: AsyncClient,
        mock_lipsync_service: MagicMock,
        sample_wav_content: bytes,
        sample_mp4_content: bytes,
    ) -> None:
        mock_lipsync_service.generate = AsyncMock(side_effect=RuntimeError("GPU error"))
        response = await client.post(
            "/api/lipsync/generate",
            files={
                "audio_file": ("test.wav", sample_wav_content, "audio/wav"),
                "video_file": ("test.mp4", sample_mp4_content, "video/mp4"),
            },
        )
        assert response.status_code == 500
        assert "エラーが発生しました" in response.json()["detail"]
