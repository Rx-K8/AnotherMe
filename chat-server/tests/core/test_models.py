from app.core.models import Gemma3Model, MockModel, Qwen3Model


class TestQwen3Model:
    def test_values(self) -> None:
        assert Qwen3Model.QWEN_4B.value == "Qwen/Qwen3-4B-Instruct-2507"
        assert Qwen3Model.QWEN_30B.value == "Qwen/Qwen3-30B-A3B-Instruct-2507"


class TestGemma3Model:
    def test_values(self) -> None:
        assert Gemma3Model.GEMMA_4B.value == "google/gemma-3-4b-it"
        assert Gemma3Model.GEMMA_27B.value == "google/gemma-3-27b-it"


class TestMockModel:
    def test_value(self) -> None:
        assert MockModel.MOCK.value == "mock"
