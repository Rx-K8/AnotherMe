import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router, demo_router
from app.tts.qwen3 import Qwen3TTSProvider

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """アプリケーション起動時の初期化処理"""
    logger.info("TTSプロバイダーの初期化を開始します...")
    app.state.tts_provider = Qwen3TTSProvider()
    logger.info("TTSプロバイダーの初期化が完了しました")

    yield

    logger.info("シャットダウン処理が完了しました")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AnotherMe TTS Server",
        lifespan=lifespan,
    )
    app.include_router(api_router)

    if demo_router is not None:
        app.include_router(demo_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()
