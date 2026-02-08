from io import BytesIO

import pytest
from app.validators.audio import validate_audio_file
from fastapi import HTTPException, UploadFile


class TestValidateAudioFile:
    async def test_validate_wav_file(self) -> None:
        content = b"fake wav content"
        upload_file = UploadFile(filename="test.wav", file=BytesIO(content))
        result_content, result_type = await validate_audio_file(upload_file)
        assert result_content == content
        assert result_type == ".wav"

    async def test_validate_mp3_file(self) -> None:
        content = b"fake mp3 content"
        upload_file = UploadFile(filename="song.mp3", file=BytesIO(content))
        result_content, result_type = await validate_audio_file(upload_file)
        assert result_content == content
        assert result_type == ".mp3"

    async def test_reject_unsupported_file_type(self) -> None:
        upload_file = UploadFile(filename="test.ogg", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400

    async def test_reject_oversized_file(self) -> None:
        large_content = b"a" * (11 * 1024 * 1024)
        upload_file = UploadFile(filename="large.wav", file=BytesIO(large_content))
        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400

    async def test_reject_empty_filename(self) -> None:
        upload_file = UploadFile(filename="", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400

    async def test_accept_exactly_max_size_file(self) -> None:
        max_size_content = b"a" * (10 * 1024 * 1024)
        upload_file = UploadFile(filename="maxsize.mp3", file=BytesIO(max_size_content))
        result_content, _ = await validate_audio_file(upload_file)
        assert len(result_content) == len(max_size_content)
