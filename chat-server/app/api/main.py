from app.api.routes import chat, health
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(
    router=health.router,
)
api_router.include_router(
    router=chat.router,
)
