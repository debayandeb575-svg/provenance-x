from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Provenance-X Backend"
    environment: str = "development"

    database_url: str = "sqlite:///./data/provenance_x.db"

    storage_dir: str = "./storage"

    max_upload_mb: int = 25

    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    signing_key_file: str = "./data/ed25519_private.pem"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def cors_list(self):
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings():
    return Settings()