from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520"))  # 8 days

settings = Settings()
