from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ADMIN_API_KEY: str

    APP_NAME: str = "Transactional Service - Realtors API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str
    AZURE_OPENAI_API_VERSION: str = "2024-08-01-preview"

    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER_NAME: str = "reference-images"

    MOCK_GENERATED_VIDEO_URL: str = (
        "https://marketingstoragecenter.blob.core.windows.net/final-generated-videos/"
        "final_podcast_videos/20260520_195939_332953d7.mp4"
        "?se=2026-05-27T20%3A02%3A37Z&sp=r&sv=2026-04-06&sr=b"
        "&sig=v1sK1bmnjHut/EJ2D1Sjg8Fg1GehijrZ7FO9lu/s3X4%3D"
    )

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
