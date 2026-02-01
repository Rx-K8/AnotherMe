import asyncio
import random
from collections.abc import AsyncGenerator

from app.llm.abc import LLMProvider
from app.schemas.chat import Message
from app.schemas.llm import LLMResponse, LLMStreamChunk


class MockLLMProvider(LLMProvider):
    """テスト・開発用のモックLLMプロバイダー。

    実際のLLM APIを呼び出さずに、アレンジしたレスポンスを返す。
    """

    GREETINGS = [
        "こんにちは！",
        "お元気ですか？",
        "ご質問ありがとうございます！",
        "なるほど、興味深いですね。",
    ]

    RESPONSES = [
        "について考えてみましょう。",
        "は非常に重要なテーマですね。",
        "に関して、いくつかのポイントがあります。",
        "というご質問、素晴らしいですね。",
    ]

    CONCLUSIONS = [
        "他にご質問があればお気軽にどうぞ！",
        "お役に立てれば幸いです。",
        "何かあればまたお聞きください。",
        "引き続きサポートいたします！",
    ]

    def __init__(
        self,
        model_name: str = "mock-model",
        stream_delay: float = 0.05,
    ) -> None:
        """モックプロバイダーを初期化する。

        Args:
            model_name: モデル名
            stream_delay: ストリーミング時のチャンク間の遅延（秒）
        """
        self.model_name = model_name
        self.stream_delay = stream_delay

    def _generate_response_text(self, user_message: str | None) -> str:
        """ユーザーメッセージに基づいてアレンジしたレスポンスを生成する。"""
        greeting = random.choice(self.GREETINGS)
        conclusion = random.choice(self.CONCLUSIONS)

        if user_message:
            # ユーザーメッセージの一部を使ってレスポンスを構築
            response_template = random.choice(self.RESPONSES)
            # メッセージが長い場合は最初の20文字を使用
            if len(user_message) > 20:
                summary = user_message[:20] + "..."
            else:
                summary = user_message
            body = f"「{summary}」{response_template}"
        else:
            body = "何かお手伝いできることはありますか？"

        return f"{greeting}\n\n{body}\n\n{conclusion}"

    async def generate(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """アレンジしたモックレスポンスを生成する。

        Args:
            messages: 会話履歴のメッセージリスト
            temperature: 生成の温度パラメータ（無視される）
            max_tokens: 生成する最大トークン数（無視される）

        Returns:
            LLMResponse: モックレスポンス
        """
        # 最後のユーザーメッセージを取得
        last_user_message = next(
            (m.content for m in reversed(messages) if m.role == "user"),
            None,
        )

        content = self._generate_response_text(last_user_message)

        return LLMResponse(
            content=content,
            finish_reason="stop",
            model=self.model_name,
        )

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[LLMStreamChunk]:
        """ストリーミング形式でモックレスポンスを生成する。

        Args:
            messages: 会話履歴のメッセージリスト
            temperature: 生成の温度パラメータ（無視される）
            max_tokens: 生成する最大トークン数（無視される）

        Yields:
            LLMStreamChunk: ストリーミング応答のチャンク
        """
        # 非ストリーミングと同じレスポンスを生成
        response = await self.generate(messages, temperature, max_tokens)
        content = response.content

        # 文字単位でストリーミング
        for i, char in enumerate(content):
            is_final = i == len(content) - 1
            yield LLMStreamChunk(
                model="mock",
                content=char,
                finish_reason="stop" if is_final else "",
                is_final=is_final,
            )
            if not is_final:
                await asyncio.sleep(self.stream_delay)
