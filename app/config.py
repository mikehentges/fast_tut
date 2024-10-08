from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENV_STATE: Optional[str] = None


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLLBACK: bool = False
    SENTRY_URL: Optional[str] = None
    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_API_DOMAIN: Optional[str] = None
    LOGTAIL_API_KEY: Optional[str] = None


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///./test.db"
    DB_FORCE_ROLLBACK: bool = True


@lru_cache()
def get_config(env_state: str) -> BaseConfig:
    configs = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig,
    }
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
print(config.model_dump())
