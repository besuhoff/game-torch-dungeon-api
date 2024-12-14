from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URL: str
    SECRET_KEY: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    class Config:
        env_file = ".env"

settings = Settings()
