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

    server_host: str = "0.0.0.0"
    server_port: int = 8002
    cors_origins: list[str] = ["*"]
    gpu_device: str = "cuda:2"
    max_audio_size_mb: int = 10
    max_video_size_mb: int = 50
    provider_name: str = "musetalk"
    use_float16: bool = True
    batch_size: int = 8


settings = Settings()
