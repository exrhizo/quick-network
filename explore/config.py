from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class CEnv(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SOURCE_FILE: Path = Path("data", "source.yml")



c_env = CEnv()
