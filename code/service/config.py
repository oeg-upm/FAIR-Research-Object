from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):

    # Database
    DB_PATH: Path = Path("api_control.db")
    DB_TIMEOUT: int = 30

    # Storage
    FILE_STORAGE_DIR: Path
    NO_TOKEN_DIRECTORY: Path
    SCORE_DIRECTORY: Path

    # Semantic resources
    METRICS_DIRECTORY: Path
    TESTS_DIRECTORY: Path
    BENCHMARKS_DIRECTORY: Path

    # MQTT
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883

    # Logging
    LOG_DIR: Path = Path("../../logs")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()