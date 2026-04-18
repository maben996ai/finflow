import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Platform(StrEnum):
    BILIBILI = "bilibili"
    YOUTUBE = "youtube"


class ContentType(StrEnum):
    VIDEO = "video"
    ARTICLE = "article"
    NEWS = "news"
    MARKET = "market"


class CrawlLogStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"


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
    feishu_webhooks: Mapped[list["FeishuWebhook"]] = relationship(back_populates="user", cascade="all, delete-orphan")


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
    __table_args__ = (
        UniqueConstraint("user_id", "platform", "platform_creator_id", name="uq_creators_user_platform_creator"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    platform: Mapped[Platform] = mapped_column(SqlEnum(Platform))
    platform_creator_id: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    profile_url: Mapped[str] = mapped_column(Text())
    avatar_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content_type: Mapped[ContentType] = mapped_column(SqlEnum(ContentType), default=ContentType.VIDEO, server_default=ContentType.VIDEO)
    starred: Mapped[bool] = mapped_column(Boolean, default=False)
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
    __table_args__ = (
        UniqueConstraint("creator_id", "platform_video_id", name="uq_videos_creator_platform_video"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("creators.id"), index=True)
    platform_video_id: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(500))
    thumbnail_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    video_url: Mapped[str] = mapped_column(Text())
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creator: Mapped[Creator] = relationship(back_populates="videos")


class FeishuWebhook(Base):
    __tablename__ = "feishu_webhooks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    webhook_url: Mapped[str] = mapped_column(Text())
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="feishu_webhooks")


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("creators.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default=CrawlLogStatus.SUCCESS)
    message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    videos_found: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creator: Mapped[Creator] = relationship(back_populates="crawl_logs")

