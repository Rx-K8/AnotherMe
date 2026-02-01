from collections.abc import AsyncGenerator
from threading import Thread

from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from app.llm.abc import LLMProvider
from app.schemas.chat import Message
from app.schemas.llm import LLMResponse, LLMStreamChunk


class Qwen3Provider(LLMProvider):
    """Qwen-3 LLMプロバイダー"""

    def __init__(self, model_name: str):
        """Qwen-3プロバイダーを初期化する。

        Args:
            model_name: モデル名
        """
        super().__init__()
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)  # type: ignore[no-untyped-call]
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype="auto", device_map="auto"
        )
        self.max_new_tokens = 16384

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
        message_dicts = [msg.to_dict() for msg in messages]
        text = self.tokenizer.apply_chat_template(
            message_dicts, tokenize=False, add_generation_prompt=True
        )

        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generation_kwargs = {
            **model_inputs,
            "max_new_tokens": self._get_validated_max_new_tokens(max_new_tokens),
        }

        if temperature is not None:
            generation_kwargs["temperature"] = temperature
            generation_kwargs["do_sample"] = True

        generated_ids = self.model.generate(**generation_kwargs)
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :].tolist()

        content = self.tokenizer.decode(output_ids, skip_special_tokens=True)

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
        message_dicts = [msg.to_dict() for msg in messages]
        text = self.tokenizer.apply_chat_template(
            message_dicts, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=True
        )

        generation_kwargs = {
            **model_inputs,
            "max_new_tokens": self._get_validated_max_new_tokens(max_new_tokens),
            "streamer": streamer,
        }

        if temperature is not None:
            generation_kwargs["temperature"] = temperature
            generation_kwargs["do_sample"] = True

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
