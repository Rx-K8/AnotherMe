from pathlib import Path

from fastapi import HTTPException, UploadFile, status

ALLOWED_MEDIA_EXTENSIONS = {".mp4", ".mov", ".jpg", ".png"}
MAX_MEDIA_FILE_SIZE = 50 * 1024 * 1024  # 50MB


async def validate_media_file(media_file: UploadFile) -> tuple[bytes, str]:
    """メディアファイルを検証し、内容と拡張子を返す.

    Args:
        media_file: アップロードされた動画/画像ファイル

    Returns:
        tuple[bytes, str]: (ファイル内容, 拡張子)

    Raises:
        HTTPException: ファイル形式が不正、サイズ超過、または空ファイルの場合
    """
    filename = media_file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_MEDIA_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Supported formats: {', '.join(sorted(ALLOWED_MEDIA_EXTENSIONS))}"
            ),
        )

    content = await media_file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    if len(content) > MAX_MEDIA_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the limit (50MB)",
        )

    return content, ext
