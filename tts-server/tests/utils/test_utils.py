import base64

from app.utils import encode_audio_base64


class TestEncodeAudioBase64:
    def test_encode_empty_bytes(self) -> None:
        result = encode_audio_base64(b"")
        assert result == ""

    def test_encode_simple_bytes(self) -> None:
        data = b"hello"
        result = encode_audio_base64(data)
        assert result == base64.b64encode(data).decode("utf-8")

    def test_encode_binary_data(self) -> None:
        data = bytes(range(256))
        result = encode_audio_base64(data)
        decoded = base64.b64decode(result)
        assert decoded == data

    def test_return_type_is_str(self) -> None:
        result = encode_audio_base64(b"test")
        assert isinstance(result, str)
