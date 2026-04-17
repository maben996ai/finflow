import os
import tempfile

from app.core.config import Settings, get_settings


def test_settings_has_default_app_name():
    s = Settings(_env_file=None)
    assert s.app_name == "FinFlow"


def test_settings_default_types():
    s = Settings(_env_file=None)
    assert isinstance(s.database_url, str)
    assert isinstance(s.redis_url, str)
    assert isinstance(s.secret_key, str)
    assert isinstance(s.access_token_expire_minutes, int)
    assert isinstance(s.youtube_api_key, str)
    assert isinstance(s.bilibili_sessdata, str)


def test_settings_access_token_default():
    s = Settings(_env_file=None)
    assert s.access_token_expire_minutes == 43200


def test_settings_reads_from_env_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("SECRET_KEY=test-secret-from-env\n")
        f.write("ACCESS_TOKEN_EXPIRE_MINUTES=60\n")
        env_path = f.name

    try:
        s = Settings(_env_file=env_path)
        assert s.secret_key == "test-secret-from-env"
        assert s.access_token_expire_minutes == 60
    finally:
        os.unlink(env_path)


def test_settings_env_overrides_default():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("YOUTUBE_API_KEY=my-youtube-key\n")
        f.write("BILIBILI_SESSDATA=my-sessdata\n")
        env_path = f.name

    try:
        s = Settings(_env_file=env_path)
        assert s.youtube_api_key == "my-youtube-key"
        assert s.bilibili_sessdata == "my-sessdata"
    finally:
        os.unlink(env_path)


def test_get_settings_returns_same_instance():
    get_settings.cache_clear()
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
