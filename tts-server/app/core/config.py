"""アプリケーション設定"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定クラス

    環境変数または.envファイルから設定を読み込む。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENABLE_DEMO: bool = False
    server_host: str
    server_port: int
    cors_origins: list[str]


settings = Settings()  # type: ignore[call-arg]
