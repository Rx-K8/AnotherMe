from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


class TestSettings:
    def test_load_from_env_vars(self) -> None:
        with patch.dict(
            "os.environ",
            {"APP_NAME": "test-app", "LLM_MODEL_NAME": "mock", "SERVER_HOST": "0.0.0.0", "SERVER_PORT": "8000", "CORS_ORIGINS": '["*"]'},
            clear=False,
        ):
            settings = Settings()  # type: ignore[call-arg]
            assert settings.app_name == "test-app"
            assert settings.llm_model_name == "mock"

    def test_missing_required_field_raises_error(self) -> None:
        """環境変数も.envも無い場合、ValidationErrorが発生する"""
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValidationError),
        ):
            Settings(_env_file=None)  # type: ignore[call-arg]


class TestGetSettings:
    def test_returns_settings_instance(self) -> None:
        get_settings.cache_clear()
        with patch.dict(
            "os.environ",
            {"APP_NAME": "test-app", "LLM_MODEL_NAME": "mock", "SERVER_HOST": "0.0.0.0", "SERVER_PORT": "8000", "CORS_ORIGINS": '["*"]'},
            clear=False,
        ):
            settings = get_settings()
            assert isinstance(settings, Settings)
        get_settings.cache_clear()
