from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.dependencies import initialize_llm_provider

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """アプリケーションのライフサイクル管理。

    起動時と終了時の処理を定義する。
    """

    logger.info("サーバー起動中: AIモデルをロードしています...")
    initialize_llm_provider()
    logger.info("AIモデルのロードが完了しました")

    yield

    logger.info("サーバーを終了します")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    return app


app = create_app()
