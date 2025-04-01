from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    APP_VERSION: Optional[str] = None
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    GEMINI_API_KEY: Optional[str] = None

    # Database settings - General
    DATABASE_TYPE: Optional[str] = "sqlalchemy"  # Options: "sqlalchemy", "mongodb"

    # SQLAlchemy settings (relational)
    SQLALCHEMY_DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///data/app.db"
    SQL_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30

    # MongoDB settings (non-relational)
    MONGODB_URL: Optional[str] = "mongodb://localhost:27017"
    MONGODB_DATABASE_NAME: Optional[str] = "app_db"

    class Config:
        env_file = ".env"


settings = Settings()
