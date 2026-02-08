"""メディア（動画/画像）ファイルバリデーションのテスト."""

from io import BytesIO

import pytest
from app.validators.media import (
    ALLOWED_MEDIA_EXTENSIONS,
    MAX_MEDIA_FILE_SIZE,
    validate_media_file,
)
from fastapi import HTTPException, UploadFile


class TestValidateMediaFile:
    # --- 正常系 ---

    async def test_valid_mp4_file(self) -> None:
        content = b"fake mp4 content"
        upload_file = UploadFile(filename="test.mp4", file=BytesIO(content))
        result_content, result_ext = await validate_media_file(upload_file)
        assert result_content == content
        assert result_ext == ".mp4"

    async def test_valid_mov_file(self) -> None:
        content = b"fake mov content"
        upload_file = UploadFile(filename="test.mov", file=BytesIO(content))
        result_content, result_ext = await validate_media_file(upload_file)
        assert result_content == content
        assert result_ext == ".mov"

    async def test_valid_jpg_file(self) -> None:
        content = b"fake jpg content"
        upload_file = UploadFile(filename="face.jpg", file=BytesIO(content))
        result_content, result_ext = await validate_media_file(upload_file)
        assert result_content == content
        assert result_ext == ".jpg"

    async def test_valid_png_file(self) -> None:
        content = b"fake png content"
        upload_file = UploadFile(filename="face.png", file=BytesIO(content))
        result_content, result_ext = await validate_media_file(upload_file)
        assert result_content == content
        assert result_ext == ".png"

    async def test_valid_uppercase_extension(self) -> None:
        content = b"fake mp4 content"
        upload_file = UploadFile(filename="test.MP4", file=BytesIO(content))
        result_content, result_ext = await validate_media_file(upload_file)
        assert result_content == content
        assert result_ext == ".mp4"

    # --- 異常系: 拡張子 ---

    async def test_reject_unsupported_extension(self) -> None:
        upload_file = UploadFile(filename="test.avi", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await validate_media_file(upload_file)
        assert exc_info.value.status_code == 400
        for ext in sorted(ALLOWED_MEDIA_EXTENSIONS):
            assert ext in str(exc_info.value.detail)

    async def test_reject_no_extension(self) -> None:
        upload_file = UploadFile(filename="testfile", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await validate_media_file(upload_file)
        assert exc_info.value.status_code == 400

    async def test_reject_empty_filename(self) -> None:
        upload_file = UploadFile(filename="", file=BytesIO(b"content"))
        with pytest.raises(HTTPException) as exc_info:
            await validate_media_file(upload_file)
        assert exc_info.value.status_code == 400

    # --- 異常系: サイズ ---

    async def test_reject_oversized_file(self) -> None:
        large_content = b"x" * (MAX_MEDIA_FILE_SIZE + 1)
        upload_file = UploadFile(filename="test.mp4", file=BytesIO(large_content))
        with pytest.raises(HTTPException) as exc_info:
            await validate_media_file(upload_file)
        assert exc_info.value.status_code == 400
        assert "50MB" in str(exc_info.value.detail)

    async def test_accept_exactly_max_size(self) -> None:
        content = b"x" * MAX_MEDIA_FILE_SIZE
        upload_file = UploadFile(filename="test.mp4", file=BytesIO(content))
        result_content, result_ext = await validate_media_file(upload_file)
        assert len(result_content) == MAX_MEDIA_FILE_SIZE
        assert result_ext == ".mp4"

    # --- 異常系: 空ファイル ---

    async def test_reject_empty_file(self) -> None:
        upload_file = UploadFile(filename="test.mp4", file=BytesIO(b""))
        with pytest.raises(HTTPException) as exc_info:
            await validate_media_file(upload_file)
        assert exc_info.value.status_code == 400
