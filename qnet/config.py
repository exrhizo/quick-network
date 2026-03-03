from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class CEnv(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BASE_DIR: Path = Path(__file__).parent.parent
    FRACTAL_MOMENT_KG: Path = BASE_DIR / "data" / "fractal_moment" / "source.yml"
    
    ACTANT_FUTURE: Path = BASE_DIR / "data" / "actant" / "sept2025.yml"
    ACTANT_FUTURE_CYTO: Path = BASE_DIR / "derived" / "actant" / "future.json"



c_env = CEnv()
