"""音声ファイルのバリデーション."""

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".wav", ".mp3"}


async def validate_audio_file(audio_file: UploadFile) -> tuple[bytes, str]:
    """音声ファイルを検証し、内容と拡張子を返す。

    Args:
        audio_file: アップロードされた音声ファイル

    Returns:
        tuple[bytes, str]: (ファイル内容, 拡張子)

    Raises:
        HTTPException: ファイル形式が不正またはサイズ超過の場合
    """
    filename = audio_file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"対応している音声形式は{', '.join(sorted(ALLOWED_EXTENSIONS))}です",
        )

    content = await audio_file.read()

    if len(content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルサイズが上限（10MB）を超えています",
        )

    return content, ext
