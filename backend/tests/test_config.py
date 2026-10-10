import secrets

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_accept_generated_secret():
    secret = secrets.token_urlsafe(48)
    settings = Settings(_env_file=None, DATABASE_URL='sqlite://', SECRET_KEY=secret)
    assert settings.SECRET_KEY == secret


def test_settings_reject_missing_secret(monkeypatch):
    monkeypatch.delenv('SECRET_KEY', raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, DATABASE_URL='sqlite://')


@pytest.mark.parametrize(
    'secret',
    [
        pytest.param('', id='missing'),
        pytest.param('short', id='short'),
        pytest.param('REPLACE_WITH_GENERATED_SECRET_AT_LEAST_32_CHARACTERS', id='placeholder'),
        pytest.param('a' * 48, id='repeated-character'),
        pytest.param('1234567890' * 4, id='sequential-digits'),
        pytest.param('password' * 6, id='predictable-word'),
        pytest.param('abcdefghijklmnopqrstuvwxyzABCDEF', id='sequential-letters'),
    ],
)
def test_settings_reject_missing_short_or_placeholder_secret(secret):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, DATABASE_URL='sqlite://', SECRET_KEY=secret)


@pytest.mark.parametrize('database_url', ['', 'REPLACE_WITH_DATABASE_CONNECTION_STRING', 'not-a-database-url'])
def test_settings_reject_unconfigured_database_url(database_url):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, DATABASE_URL=database_url, SECRET_KEY=secrets.token_urlsafe(48))
