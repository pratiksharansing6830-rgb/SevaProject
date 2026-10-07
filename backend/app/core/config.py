from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    DATABASE_URL: str = 'postgresql+psycopg://sahaayak:sahaayak@localhost:5432/sahaayak'
    SECRET_KEY: str = 'development-secret-key-change-me'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = 'HS256'
    FRONTEND_URL: str = 'http://localhost:5173'


settings = Settings()
