from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from app.schemas.chat import Message
from app.schemas.llm import LLMResponse, LLMStreamChunk


class LLMProvider(ABC):
    """
    LLMプロバイダーの抽象基底クラス

    全てのLLMプロバイダー（OpenAI, Anthropic, ローカルモデル等）は
    このクラスを継承して実装する。
    """

    def __init__(self) -> None:
        """LLMプロバイダーを初期化する。

        サブクラスは__init__内でself.max_new_tokensを設定する必要がある。
        """
        self.max_new_tokens: int

    def _get_validated_max_new_tokens(self, max_new_tokens: int | None) -> int:
        """max_new_tokensをバリデートし、モデルの最大値を超えない値を返す。

        Args:
            max_new_tokens: 指定された最大トークン数

        Returns:
            バリデートされた最大トークン数
        """
        if max_new_tokens is not None:
            return min(max_new_tokens, self.max_new_tokens)
        return self.max_new_tokens

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_new_tokens: int | None = None,
    ) -> LLMResponse:
        """
        メッセージリストに基づいて応答を生成する

        Args:
            messages: 会話履歴のメッセージリスト
            temperature: 生成の温度パラメータ（0.0-2.0）
            max_new_tokens: 生成する最大トークン数

        Returns:
            LLMResponse: 生成された応答
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_new_tokens: int | None = None,
    ) -> AsyncGenerator[LLMStreamChunk]:
        """
        ストリーミング形式で応答を生成する

        Args:
            messages: 会話履歴のメッセージリスト
            temperature: 生成の温度パラメータ（0.0-2.0）
            max_new_tokens: 生成する最大トークン数

        Yields:
            LLMStreamChunk: ストリーミング応答のチャンク
        """
        yield  # type: ignore[misc]
