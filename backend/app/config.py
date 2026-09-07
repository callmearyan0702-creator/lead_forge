"""
Centralized application configuration.

Everything environment-specific (DB connection, allowed origins, upload
limits) lives here so the rest of the codebase never reads os.environ
directly. This is also the natural place to plug in future settings
(auth secrets, feature flags, external API keys) without touching
business logic elsewhere.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Defaults to local Postgres; override in .env. SQLite works too since
    # everything goes through SQLAlchemy's ORM layer (no Postgres-only SQL).bbbb
    database_url: str = "postgresql://postgres:postgres@localhost:5432/lead_intelligence"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Upload constraints. Keeping these centralized makes it trivial to
    # tighten/loosen limits later (e.g. once auth + per-user quotas exist).
    max_upload_rows: int = 20000
    max_upload_mb: int = 10

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
