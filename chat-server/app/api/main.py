from fastapi import APIRouter

from app.api.routes import chat, health

api_router = APIRouter()

api_router.include_router(
    router=health.router,
)
api_router.include_router(
    router=chat.router,
)
