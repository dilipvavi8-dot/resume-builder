"""Application configuration using environment variables"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_NAME: str = "Resume Builder API"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # AWS (populated from Secrets Manager / env in EKS)
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # Secret Manager (no hardcoded secrets)
    SECRET_NAME: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
