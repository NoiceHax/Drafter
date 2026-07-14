"""Application settings loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_JWT_DEFAULT = "dev-insecure-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    database_url: str = "postgresql+psycopg://user:password@localhost:5432/copilot"

    # LLM provider
    llm_provider: str = "nvidia"
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.1-8b-instruct"
    # Per-request timeout (seconds) for LLM calls; a stalled call fails fast.
    nvidia_timeout: float = 90.0

    # Search provider
    search_provider: str = "none"  # none | tavily | brave | serper
    tavily_api_key: str = ""
    brave_search_api_key: str = ""
    serper_api_key: str = ""

    # Image search provider
    image_search_provider: str = "wikimedia"  # wikimedia | pexels | unsplash
    pexels_api_key: str = ""
    unsplash_access_key: str = ""

    # App
    frontend_url: str = "http://localhost:3000"
    words_per_minute: int = 150

    # Auth
    jwt_secret: str = _INSECURE_JWT_DEFAULT
    jwt_expire_hours: int = 720  # 30 days
    alpha_emails: str = ""  # comma-separated emails that skip the password step
    # Set to 1/true only for local dev to allow the insecure default JWT secret.
    allow_insecure_jwt: bool = False

    def require_secure_secret(self) -> None:
        """Fail fast if the JWT secret was left at the insecure default.

        The whole per-user isolation model rests on token integrity, so a
        deployment must set a real JWT_SECRET. Local dev can opt out with
        ALLOW_INSECURE_JWT=1.
        """
        insecure = (not self.jwt_secret) or self.jwt_secret == _INSECURE_JWT_DEFAULT
        if insecure and not self.allow_insecure_jwt:
            raise RuntimeError(
                "JWT_SECRET is unset or using the insecure default. Set a strong, "
                "random JWT_SECRET in the environment before starting the server "
                "(or set ALLOW_INSECURE_JWT=1 for local development only)."
            )

    # Postgres schema all tables live in (isolates this app on a shared database).
    db_schema: str = "copilot"

    @property
    def alpha_email_set(self) -> set[str]:
        return {e.strip().lower() for e in self.alpha_emails.split(",") if e.strip()}

    @property
    def sqlalchemy_url(self) -> str:
        """Normalize the DB URL to use the installed psycopg (v3) driver.

        Accepts plain ``postgresql://`` (common from hosting providers like Neon)
        and rewrites it to ``postgresql+psycopg://`` so SQLAlchemy does not fall
        back to psycopg2.
        """
        url = self.database_url
        if url.startswith("postgresql+"):
            return url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    @property
    def research_enabled(self) -> bool:
        """Research mode is only enabled when a real search provider is configured."""
        if self.search_provider == "tavily":
            return bool(self.tavily_api_key)
        if self.search_provider == "brave":
            return bool(self.brave_search_api_key)
        if self.search_provider == "serper":
            return bool(self.serper_api_key)
        return False

    @property
    def llm_configured(self) -> bool:
        return bool(self.nvidia_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
