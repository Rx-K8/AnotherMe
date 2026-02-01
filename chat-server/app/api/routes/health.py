from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health", summary="ヘルスチェック", description="APIのヘルスチェックを行います"
)
async def health() -> dict[str, str]:
    """
    ヘルスチェックエンドポイント

    Returns:
        dict: ヘルスステータス
    """
    return {"status": "ok"}
