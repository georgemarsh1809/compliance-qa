from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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
    embedding_model: str = "voyage-3"


@lru_cache
def get_settings() -> Settings:
    return Settings()
