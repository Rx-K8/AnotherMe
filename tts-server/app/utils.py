"""ユーティリティ関数"""

import base64


def encode_audio_base64(audio_data: bytes) -> str:
    """音声データをBase64エンコードする"""
    return base64.b64encode(audio_data).decode("utf-8")
