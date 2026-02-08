"""Qwen3-TTS Voice Clone プロバイダー実装

Voice Cloneモード専用: 参照音声から声をクローンして音声合成を行う
https://github.com/QwenLM/Qwen3-TTS
"""

import io
import os
import tempfile

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel


class Qwen3TTSProvider:  # pragma: no cover
    """Qwen3-TTS Voice Clone プロバイダー

    Qwen3-TTS-12Hz-1.7B-Base モデルを使用したVoice Clone専用の音声合成。
    参照音声（ref_audio）とそのテキスト（ref_text）から声をクローンし、
    任意のテキストをその声で合成する。
    """

    def __init__(self) -> None:
        self.model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            device_map="cuda:0",
            dtype=torch.bfloat16,
        )

    async def synthesize_with_reference(
        self,
        text: str,
        ref_audio_bytes: bytes,
        ref_audio_ext: str,
        ref_text: str,
        speed: float = 1.0,
    ) -> bytes:
        # create_voice_clone_prompt APIがファイルパスを要求するため一時ファイルを使用
        tmp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ref_audio_ext) as tmp:
                tmp.write(ref_audio_bytes)
                tmp_path = tmp.name

            voice_clone_prompt = self.model.create_voice_clone_prompt(
                ref_audio=tmp_path,
                ref_text=ref_text,
            )

            wavs, sr = self.model.generate_voice_clone(
                text=text,
                language="Japanese",
                voice_clone_prompt=voice_clone_prompt,
            )

            audio_data = wavs[0] if isinstance(wavs, list) else wavs

            buffer = io.BytesIO()
            sf.write(buffer, audio_data, sr, format="WAV")
            return buffer.getvalue()
        finally:
            if tmp_path is not None:
                os.unlink(tmp_path)
