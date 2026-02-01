from app.core.models import Gemma3Model, MockModel, Qwen3Model
from app.llm import Gemma3Provider, LLMProvider, MockLLMProvider, Qwen3Provider


def get_provider_name(model_name: str) -> str:
    """モデル名からプロバイダー名を取得する"""
    if model_name in {m.value for m in Qwen3Model}:
        return "qwen3"
    elif model_name in {m.value for m in Gemma3Model}:
        return "gemma3"
    elif model_name in {m.value for m in MockModel}:
        return "mock"
    else:
        raise ValueError(f"不明なモデル名: {model_name}")


def create_provider(model_name: str) -> LLMProvider:
    """モデル名から対応するLLMプロバイダーのインスタンスを生成する"""
    provider_name = get_provider_name(model_name)

    providers = {
        "qwen3": Qwen3Provider,
        "gemma3": Gemma3Provider,
        "mock": MockLLMProvider,
    }

    provider_class = providers[provider_name]
    return provider_class(model_name=model_name)  # type: ignore[no-any-return]
