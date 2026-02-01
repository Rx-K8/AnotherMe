from fastapi import APIRouter

from app.api.routes import demo, health, tts
from app.core.config import settings

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(tts.router)

# デモUIルーター（ENABLE_DEMO=trueの場合のみ有効）
demo_router: APIRouter | None = None
if settings.ENABLE_DEMO:
    demo_router = demo.router
