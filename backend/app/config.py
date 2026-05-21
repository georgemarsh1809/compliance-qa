from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    anthropic_api_key: str
    voyage_api_key: str
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "compliance-qa"
    aws_region: str = "eu-west-2"
    s3_corpus_bucket: str
    s3_index_bucket: str
    log_level: str = "INFO"
    chat_model: str = "claude-haiku-4-5-20251001"
    judge_model: str = "claude-sonnet-4-6"
    embedding_model: str = "voyage-3.5"


@lru_cache
def get_settings() -> Settings:
    return Settings()
