import pytest

from app.core.models import Gemma3Model, MockModel, Qwen3Model
from app.llm.factory import create_provider, get_provider_name
from app.llm.mock import MockLLMProvider


class TestGetProviderName:
    def test_qwen3_model(self) -> None:
        assert get_provider_name(Qwen3Model.QWEN_4B.value) == "qwen3"

    def test_gemma3_model(self) -> None:
        assert get_provider_name(Gemma3Model.GEMMA_4B.value) == "gemma3"

    def test_mock_model(self) -> None:
        assert get_provider_name(MockModel.MOCK.value) == "mock"

    def test_unknown_model_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="不明なモデル名"):
            get_provider_name("unknown-model")


class TestCreateProvider:
    def test_create_mock_provider(self) -> None:
        provider = create_provider("mock")
        assert isinstance(provider, MockLLMProvider)
