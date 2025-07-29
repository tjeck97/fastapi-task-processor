import os
from enum import Enum
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class AppEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


# Used to determine which settings class to instantiate
ENVIRONMENT = os.getenv("ENVIRONMENT", AppEnvironment.DEVELOPMENT.value)


class CommonSettings(BaseSettings):
    APP_NAME: str = "FastAPI Task Processor"
    DEBUG: bool = False
    ENVIRONMENT: str = ENVIRONMENT
    TESTING: bool = False

    DATABASE_URL: str
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class DevelopmentSettings(CommonSettings):
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+psycopg2://trevoreckler@localhost:5432/taskdb"


class StagingSettings(CommonSettings):
    DEBUG: bool = False
    # DATABASE_URL must be passed via environment


class ProductionSettings(CommonSettings):
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["https://your-production-domain.com"]
    # DATABASE_URL must be passed via environment


class TestingSettings(CommonSettings):
    DEBUG: bool = True
    TESTING: bool = True
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/test_taskdb"


@lru_cache()
def get_settings() -> CommonSettings:
    try:
        env = AppEnvironment(ENVIRONMENT)
    except ValueError:
        raise ValueError(f"Invalid ENVIRONMENT: {ENVIRONMENT}")

    match env:
        case AppEnvironment.DEVELOPMENT:
            return DevelopmentSettings()
        case AppEnvironment.STAGING:
            return StagingSettings()
        case AppEnvironment.PRODUCTION:
            return ProductionSettings()
        case AppEnvironment.TESTING:
            return TestingSettings()
