from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.models import User, UserSettings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def ensure_dev_account() -> None:
    if not settings.dev_account_password:
        return

    async with AsyncSessionLocal() as session:
        existing_user = await session.scalar(
            select(User).where(User.email == settings.dev_account_email)
        )
        if existing_user is not None:
            return

        user = User(
            email=settings.dev_account_email,
            password_hash=get_password_hash(settings.dev_account_password),
            display_name=settings.dev_account_display_name,
        )
        session.add(user)
        await session.flush()
        session.add(UserSettings(user_id=user.id))
        await session.commit()


async def init_db() -> None:
    if settings.database_url.startswith("sqlite"):
        sqlite_path = settings.database_url.removeprefix("sqlite+aiosqlite:///")
        Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    await ensure_dev_account()
