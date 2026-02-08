"""APIルーター集約"""

from fastapi import APIRouter

from app.api.routes import health, lipsync

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(lipsync.router)
