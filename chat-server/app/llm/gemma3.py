from collections.abc import AsyncGenerator
from threading import Thread
from typing import Any

from transformers import (
    AutoProcessor,
    Gemma3ForConditionalGeneration,
    TextIteratorStreamer,
)

from app.llm.abc import LLMProvider
from app.schemas.chat import Message
from app.schemas.llm import LLMResponse, LLMStreamChunk


class Gemma3Provider(LLMProvider):
    """Gemma 3 LLMプロバイダー"""

    def __init__(self, model_name: str):
        """Gemma 3プロバイダーを初期化する。

        Args:
            model_name: モデル名
        """
        super().__init__()
        self.model_name = model_name
        self.processor = AutoProcessor.from_pretrained(model_name)  # type: ignore[no-untyped-call]
        self.model = Gemma3ForConditionalGeneration.from_pretrained(
            model_name, device_map="auto"
        ).eval()
        self.max_new_tokens = 8192

    def _prepare_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        """メッセージをGemma 3のチャットテンプレート形式に変換する。

        Args:
            messages: チャットメッセージのリスト

        Returns:
            Gemma 3のチャットテンプレート形式のメッセージリスト
        """
        formatted_messages: list[dict[str, Any]] = []

        for msg in messages:
            formatted_messages.append(
                {
                    "role": msg.role,
                    "content": [{"type": "text", "text": msg.content}],
                }
            )

        return formatted_messages

    async def generate(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_new_tokens: int | None = None,
    ) -> LLMResponse:
        """メッセージリストに基づいて応答を生成する。

        Args:
            messages: 会話履歴のメッセージリスト
            temperature: 生成の温度パラメータ
            max_new_tokens: 生成する最大トークン数

        Returns:
            LLMResponse: 生成された応答
        """
        formatted_messages = self._prepare_messages(messages)

        inputs = self.processor.apply_chat_template(
            formatted_messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)

        input_len = inputs["input_ids"].shape[-1]

        generation_kwargs = {
            **inputs,
            "max_new_tokens": self._get_validated_max_new_tokens(max_new_tokens),
        }

        if temperature is not None:
            generation_kwargs["temperature"] = temperature
            generation_kwargs["do_sample"] = True
        else:
            generation_kwargs["do_sample"] = False

        generated_ids = self.model.generate(**generation_kwargs)
        output_ids = generated_ids[0][input_len:]

        content = self.processor.decode(output_ids, skip_special_tokens=True)

        return LLMResponse(
            content=content,
            finish_reason="stop",
            model=self.model_name,
        )

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float | None = None,
        max_new_tokens: int | None = None,
    ) -> AsyncGenerator[LLMStreamChunk]:
        """ストリーミング形式で応答を生成する。

        Args:
            messages: 会話履歴のメッセージリスト
            temperature: 生成の温度パラメータ
            max_new_tokens: 生成する最大トークン数

        Yields:
            LLMStreamChunk: ストリーミング応答のチャンク
        """
        formatted_messages = self._prepare_messages(messages)

        inputs = self.processor.apply_chat_template(
            formatted_messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)

        streamer = TextIteratorStreamer(
            self.processor.tokenizer, skip_prompt=True, skip_special_tokens=True
        )

        generation_kwargs = {
            **inputs,
            "max_new_tokens": self._get_validated_max_new_tokens(max_new_tokens),
            "streamer": streamer,
        }

        if temperature is not None:
            generation_kwargs["temperature"] = temperature
            generation_kwargs["do_sample"] = True
        else:
            generation_kwargs["do_sample"] = False

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        for new_text in streamer:
            # 空文字が送られてくることがあるため、無視する。
            # 空文字が生成されるのは正常な動作。
            if new_text:
                yield LLMStreamChunk(
                    content=new_text,
                    finish_reason="",
                    is_final=False,
                    model=self.model_name,
                )

        yield LLMStreamChunk(
            content="",
            finish_reason="stop",
            is_final=True,
            model=self.model_name,
        )
