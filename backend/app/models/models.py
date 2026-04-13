import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Platform(StrEnum):
    BILIBILI = "bilibili"
    YOUTUBE = "youtube"


def uuid_str() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creators: Mapped[list["Creator"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    settings: Mapped["UserSettings | None"] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True)
    feishu_webhook_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="settings")


class Creator(Base):
    __tablename__ = "creators"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    platform: Mapped[Platform] = mapped_column(SqlEnum(Platform))
    platform_creator_id: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    profile_url: Mapped[str] = mapped_column(Text())
    avatar_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship(back_populates="creators")
    videos: Mapped[list["Video"]] = relationship(back_populates="creator", cascade="all, delete-orphan")
    crawl_logs: Mapped[list["CrawlLog"]] = relationship(back_populates="creator", cascade="all, delete-orphan")


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("creators.id"), index=True)
    platform_video_id: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(500))
    thumbnail_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    video_url: Mapped[str] = mapped_column(Text())
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creator: Mapped[Creator] = relationship(back_populates="videos")


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("creators.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="success")
    message: Mapped[str] = mapped_column(Text(), default="Initialized placeholder crawl log")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creator: Mapped[Creator] = relationship(back_populates="crawl_logs")

