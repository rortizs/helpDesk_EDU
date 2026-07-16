from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Runtime configuration loaded from environment or a local .env file."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./helpdesk.db"
    jwt_secret: str = "development-only-change-this"
    jwt_expire_hours: int = 8

settings = Settings()
