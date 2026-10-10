from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
        hide_input_in_errors=True,
    )

    DATABASE_URL: str = Field(min_length=1)
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = 'HS256'
    FRONTEND_URL: str = 'http://localhost:5173'

    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if value.strip().lower().startswith(('replace-', 'replace_', 'your-database')):
            raise ValueError('DATABASE_URL must be configured with a valid database connection.')
        try:
            make_url(value)
        except ArgumentError as exc:
            raise ValueError('DATABASE_URL must be a valid SQLAlchemy database URL.') from exc
        return value

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized.startswith(('change-me', 'replace-', 'replace_', 'your-secret')):
            raise ValueError('SECRET_KEY must be a generated secret, not a placeholder.')
        if len(value.strip()) < 32:
            raise ValueError('SECRET_KEY must contain at least 32 non-whitespace characters.')
        predictable_sequences = (
            '0123456789',
            'abcdefghijklmnopqrstuvwxyz',
            'qwertyuiop',
            'password',
            'letmein',
            'admin',
            'secret',
            'changeme',
        )
        if len(set(normalized)) < 12 or any(sequence in normalized for sequence in predictable_sequences):
            raise ValueError('SECRET_KEY must be securely generated and not an obvious predictable value.')
        return value


settings = Settings()
