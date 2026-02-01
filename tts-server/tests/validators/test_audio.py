from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.validators import MAX_AUDIO_SIZE_BYTES, validate_audio_file


class TestValidateAudioFile:
    async def test_valid_wav_file(self) -> None:
        content = b"fake wav content"
        upload_file = UploadFile(filename="test.wav", file=BytesIO(content))
        result_content, result_ext = await validate_audio_file(upload_file)
        assert result_content == content
        assert result_ext == ".wav"

    async def test_valid_wav_uppercase_extension(self) -> None:
        content = b"fake wav content"
        upload_file = UploadFile(filename="test.WAV", file=BytesIO(content))
        result_content, result_ext = await validate_audio_file(upload_file)
        assert result_content == content
        assert result_ext == ".wav"

    async def test_valid_mp3_file(self) -> None:
        content = b"fake mp3 content"
        upload_file = UploadFile(filename="test.mp3", file=BytesIO(content))
        result_content, result_ext = await validate_audio_file(upload_file)
        assert result_content == content
        assert result_ext == ".mp3"

    async def test_valid_mp3_uppercase_extension(self) -> None:
        content = b"fake mp3 content"
        upload_file = UploadFile(filename="test.MP3", file=BytesIO(content))
        result_content, result_ext = await validate_audio_file(upload_file)
        assert result_content == content
        assert result_ext == ".mp3"

    async def test_reject_unsupported_extension(self) -> None:
        upload_file = UploadFile(filename="test.ogg", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400
        assert ".mp3" in str(exc_info.value.detail)
        assert ".wav" in str(exc_info.value.detail)

    async def test_reject_no_extension(self) -> None:
        upload_file = UploadFile(filename="testfile", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400

    async def test_reject_empty_filename(self) -> None:
        upload_file = UploadFile(filename="", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400

    async def test_reject_oversized_file(self) -> None:
        large_content = b"x" * (MAX_AUDIO_SIZE_BYTES + 1)
        upload_file = UploadFile(filename="test.wav", file=BytesIO(large_content))
        with pytest.raises(HTTPException) as exc_info:
            await validate_audio_file(upload_file)
        assert exc_info.value.status_code == 400
        assert "10MB" in str(exc_info.value.detail)

    async def test_accept_exactly_max_size(self) -> None:
        content = b"x" * MAX_AUDIO_SIZE_BYTES
        upload_file = UploadFile(filename="test.wav", file=BytesIO(content))
        result_content, result_ext = await validate_audio_file(upload_file)
        assert len(result_content) == MAX_AUDIO_SIZE_BYTES
        assert result_ext == ".wav"
