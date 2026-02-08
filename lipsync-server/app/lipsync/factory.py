"""リップシンクプロバイダーのファクトリー"""

from app.lipsync.abc import LipsyncProvider
from app.lipsync.mock import MockLipsyncProvider


def create_provider(provider_name: str) -> LipsyncProvider:
    """プロバイダー名からLipsyncProviderインスタンスを生成する

    Args:
        provider_name: プロバイダー名 ("mock" など)

    Raises:
        ValueError: 不明なプロバイダー名の場合
    """
    providers: dict[str, type[LipsyncProvider]] = {
        "mock": MockLipsyncProvider,
    }

    provider_class = providers.get(provider_name)
    if provider_class is None:
        available = ", ".join(sorted(providers.keys()))
        raise ValueError(
            f"不明なプロバイダー名: {provider_name!r} (利用可能: {available})"
        )

    return provider_class()
