"""APIルーター集約"""

from fastapi import APIRouter

from app.api.routes import demo, health, lipsync
from app.core.config import settings

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(lipsync.router)

demo_router: APIRouter | None = None
if settings.enable_demo:
    demo_router = demo.router
