from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient


class TestVoiceCloneEndpoint:
    """POST /api/tts/voice-clone のテスト"""

    async def test_voice_clone_success(
        self,
        client: AsyncClient,
        mock_tts_provider: MagicMock,
        sample_wav_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.wav", sample_wav_content, "audio/wav")},
            data={"input": "こんにちは", "ref_text": "参照テキスト", "speed": "1.0"},
        )
        assert response.status_code == 200
        assert "audio_data" in response.json()
        mock_tts_provider.synthesize_with_reference.assert_called_once()

    async def test_voice_clone_with_custom_speed(
        self,
        client: AsyncClient,
        mock_tts_provider: MagicMock,
        sample_wav_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.wav", sample_wav_content, "audio/wav")},
            data={"input": "テスト", "ref_text": "参照", "speed": "1.5"},
        )
        assert response.status_code == 200
        call_kwargs = mock_tts_provider.synthesize_with_reference.call_args.kwargs
        assert call_kwargs["speed"] == 1.5

    async def test_voice_clone_accepts_mp3_file(
        self,
        client: AsyncClient,
        mock_tts_provider: MagicMock,
        sample_wav_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.mp3", sample_wav_content, "audio/mpeg")},
            data={"input": "テスト", "ref_text": "参照"},
        )
        assert response.status_code == 200
        call_kwargs = mock_tts_provider.synthesize_with_reference.call_args.kwargs
        assert call_kwargs["ref_audio_ext"] == ".mp3"

    async def test_voice_clone_rejects_unsupported_format(
        self,
        client: AsyncClient,
        sample_wav_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.ogg", sample_wav_content, "audio/ogg")},
            data={"input": "テスト", "ref_text": "参照"},
        )
        assert response.status_code == 400
        assert ".mp3" in response.json()["detail"]
        assert ".wav" in response.json()["detail"]

    async def test_voice_clone_rejects_large_file(
        self,
        client: AsyncClient,
        large_file_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.wav", large_file_content, "audio/wav")},
            data={"input": "テスト", "ref_text": "参照"},
        )
        assert response.status_code == 400
        assert "10MB" in response.json()["detail"]

    async def test_voice_clone_missing_audio_file(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.post(
            "/api/tts/voice-clone",
            data={"input": "テスト", "ref_text": "参照"},
        )
        assert response.status_code == 422

    async def test_voice_clone_missing_input(
        self,
        client: AsyncClient,
        sample_wav_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.wav", sample_wav_content, "audio/wav")},
            data={"ref_text": "参照"},
        )
        assert response.status_code == 422

    async def test_voice_clone_missing_ref_text(
        self,
        client: AsyncClient,
        sample_wav_content: bytes,
    ) -> None:
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.wav", sample_wav_content, "audio/wav")},
            data={"input": "テスト"},
        )
        assert response.status_code == 422

    async def test_voice_clone_provider_value_error(
        self,
        client: AsyncClient,
        mock_tts_provider: MagicMock,
        sample_wav_content: bytes,
    ) -> None:
        mock_tts_provider.synthesize_with_reference = AsyncMock(
            side_effect=ValueError("無効なパラメータ")
        )
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.wav", sample_wav_content, "audio/wav")},
            data={"input": "テスト", "ref_text": "参照"},
        )
        assert response.status_code == 400

    async def test_voice_clone_provider_internal_error(
        self,
        client: AsyncClient,
        mock_tts_provider: MagicMock,
        sample_wav_content: bytes,
    ) -> None:
        mock_tts_provider.synthesize_with_reference = AsyncMock(
            side_effect=RuntimeError("GPU error")
        )
        response = await client.post(
            "/api/tts/voice-clone",
            files={"audio_file": ("test.wav", sample_wav_content, "audio/wav")},
            data={"input": "テスト", "ref_text": "参照"},
        )
        assert response.status_code == 500
        assert "エラーが発生しました" in response.json()["detail"]
