import pytest
from app.lipsync.factory import create_provider
from app.lipsync.mock import MockLipsyncProvider


class TestCreateProvider:
    @pytest.mark.unit
    def test_create_mock_provider(self) -> None:
        provider = create_provider("mock")
        assert isinstance(provider, MockLipsyncProvider)

    @pytest.mark.unit
    def test_unknown_provider_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="unknown"):
            create_provider("unknown")

    @pytest.mark.unit
    def test_empty_name_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            create_provider("")
