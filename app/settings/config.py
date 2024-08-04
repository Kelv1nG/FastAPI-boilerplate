from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


class GlobalConfig(BaseConfig):
    DATABASE_URL: str
    DB_FORCE_ROLL_BACK: bool = False


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="TEST_")


@lru_cache
def get_config(env_state: str):
    configs = {"DEV": DevConfig, "TEST": TestConfig, "PROD": GlobalConfig}
    return configs[env_state]()


settings = get_config(BaseConfig().ENV_STATE)
