"""設定クラスのテスト"""

import pytest
from app.core.config import Settings


class TestSettings:
    @pytest.mark.unit
    def test_default_provider_name(self) -> None:
        s = Settings()
        assert s.provider_name == "mock"
