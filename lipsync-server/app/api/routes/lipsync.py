"""リップシンク生成APIルート"""

import logging

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from app.api.schema import LipsyncErrorResponse, LipsyncResponse, ParsingMode
from app.services.lipsync_service import LipsyncService
from app.validators.audio import validate_audio_file
from app.validators.media import validate_media_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lipsync", tags=["Lipsync"])


def _get_lipsync_service(request: Request) -> LipsyncService:
    return request.app.state.lipsync_service  # type: ignore[no-any-return]


@router.post(
    "/generate",
    response_model=LipsyncResponse,
    responses={
        400: {"model": LipsyncErrorResponse, "description": "不正なリクエスト"},
        500: {"model": LipsyncErrorResponse, "description": "内部サーバーエラー"},
    },
    summary="リップシンク動画生成",
    description=(
        "音声と動画/画像からリップシンク動画を生成します。"
        "対応形式: WAV/MP3 + MP4/MOV/JPG/PNG"
    ),
)
async def generate_lipsync(
    request: Request,
    audio_file: UploadFile = File(..., description="音声ファイル（WAV/MP3形式）"),
    video_file: UploadFile = File(
        ..., description="動画/画像ファイル（MP4/MOV/JPG/PNG形式）"
    ),
    bbox_shift: int = Form(default=0, description="バウンディングボックスのシフト量"),
    extra_margin: int = Form(default=10, description="顔領域の追加マージン"),
    parsing_mode: ParsingMode = Form(
        default=ParsingMode.JAW, description="顔パースモード"
    ),
) -> LipsyncResponse:
    try:
        service = _get_lipsync_service(request)
        audio_bytes, audio_ext = await validate_audio_file(audio_file)
        video_bytes, video_ext = await validate_media_file(video_file)

        result = await service.generate(
            audio_bytes=audio_bytes,
            audio_ext=audio_ext,
            video_bytes=video_bytes,
            video_ext=video_ext,
            bbox_shift=bbox_shift,
            extra_margin=extra_margin,
            parsing_mode=parsing_mode.value,
        )

        return LipsyncResponse(
            video_data=result.video_base64,
            duration_seconds=result.duration_seconds,
            processing_time_ms=result.processing_time_ms,
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.error("不正なリクエストパラメータ: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("リップシンク生成中にエラーが発生しました: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"リップシンク生成中にエラーが発生しました: {e!s}",
        )
