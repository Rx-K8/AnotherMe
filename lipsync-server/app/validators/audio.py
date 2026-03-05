from pathlib import Path

from fastapi import HTTPException, UploadFile

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3"}
MAX_AUDIO_FILE_SIZE = 10 * 1024 * 1024


async def validate_audio_file(audio_file: UploadFile) -> tuple[bytes, str]:
    filename = audio_file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported audio file type.")

    content = await audio_file.read()
    if len(content) > MAX_AUDIO_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail="Audio file size exceeds the maximum limit."
        )
    return content, ext
