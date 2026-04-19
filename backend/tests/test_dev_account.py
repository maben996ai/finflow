from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import database
from app.models.models import User, UserSettings


class TestEnsureDevAccount:
    async def test_creates_dev_account_when_password_is_configured(self, db, monkeypatch):
        session_factory = async_sessionmaker(db.bind, expire_on_commit=False, class_=AsyncSession)
        monkeypatch.setattr(database, "AsyncSessionLocal", session_factory)
        monkeypatch.setattr(database.settings, "dev_account_email", "maben996@gmail.com")
        monkeypatch.setattr(database.settings, "dev_account_display_name", "maben996")
        monkeypatch.setattr(database.settings, "dev_account_password", "password123")

        await database.ensure_dev_account()

        user = await db.scalar(select(User).where(User.email == "maben996@gmail.com"))
        settings = await db.scalar(select(UserSettings).where(UserSettings.user_id == user.id))

        assert user is not None
        assert user.display_name == "maben996"
        assert settings is not None

    async def test_skips_creation_when_password_is_blank(self, db, monkeypatch):
        session_factory = async_sessionmaker(db.bind, expire_on_commit=False, class_=AsyncSession)
        monkeypatch.setattr(database, "AsyncSessionLocal", session_factory)
        monkeypatch.setattr(database.settings, "dev_account_email", "maben996@gmail.com")
        monkeypatch.setattr(database.settings, "dev_account_display_name", "maben996")
        monkeypatch.setattr(database.settings, "dev_account_password", "")

        await database.ensure_dev_account()

        user = await db.scalar(select(User).where(User.email == "maben996@gmail.com"))
        assert user is None
