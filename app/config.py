from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./test.db"
    redis_url: str = "redis://localhost:6379"
    
    # JWT settings for auth (Sprint 5)
    jwt_secret_key: str = "changeme-in-production-min-32-chars!"
    jwt_token_lifetime_seconds: int = 86400  # 24 hours
    
    # Invite system
    invite_code_prefix: str = "NEXUS"


settings = Settings()
