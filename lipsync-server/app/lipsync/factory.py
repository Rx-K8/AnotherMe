"""リップシンクプロバイダーのファクトリー"""

from pathlib import Path

from app.core.config import settings
from app.lipsync.abc import LipsyncProvider
from app.lipsync.mock import MockLipsyncProvider


def create_provider(provider_name: str) -> LipsyncProvider:
    """プロバイダー名からLipsyncProviderインスタンスを生成する

    Args:
        provider_name: プロバイダー名 ("mock", "musetalk" など)

    Raises:
        ValueError: 不明なプロバイダー名の場合
    """
    if provider_name == "musetalk":
        from app.lipsync.musetalk_provider import MuseTalkProvider

        return MuseTalkProvider(
            device=settings.gpu_device,
            model_dir=str(
                Path(__file__).resolve().parents[2] / "submodules" / "MuseTalk"
            ),
        )

    providers: dict[str, type[LipsyncProvider]] = {
        "mock": MockLipsyncProvider,
    }

    provider_class = providers.get(provider_name)
    if provider_class is None:
        available = ", ".join(sorted([*providers.keys(), "musetalk"]))
        raise ValueError(
            f"不明なプロバイダー名: {provider_name!r} (利用可能: {available})"
        )

    return provider_class()
