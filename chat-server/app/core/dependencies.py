from app.core.config import get_settings
from app.llm.abc import LLMProvider
from app.llm.factory import create_provider
from app.services.chat_server import ChatServe

# グローバルなLLMプロバイダーインスタンス
# サーバー起動時に初期化される
_llm_provider: LLMProvider | None = None


def initialize_llm_provider() -> None:
    """LLMプロバイダーを初期化する。

    サーバー起動時に一度だけ呼び出される。
    モデルのロードはこのタイミングで行われる。
    設定に基づいて使用するプロバイダーを決定する。
    """
    global _llm_provider
    if _llm_provider is None:
        settings = get_settings()
        _llm_provider = create_provider(settings.llm_model_name)


def get_llm_provider() -> LLMProvider:
    """LLMプロバイダーのインスタンスを取得する。

    Returns:
        LLMProvider: LLMプロバイダーインスタンス

    Raises:
        RuntimeError: プロバイダーが初期化されていない場合
    """
    if _llm_provider is None:
        raise RuntimeError(
            "LLMプロバイダーが初期化されていません。"
            "アプリケーション起動時にinitialize_llm_provider()を呼び出してください。"
        )
    return _llm_provider


def get_chat_service() -> ChatServe:
    """ChatServeインスタンスを取得する。

    依存性逆転原則(DIP)に従い、具体的なLLMプロバイダーの実装は
    get_llm_provider関数で解決される。

    Returns:
        ChatServe: チャットサービスインスタンス
    """
    return ChatServe(llm_provider=get_llm_provider())
