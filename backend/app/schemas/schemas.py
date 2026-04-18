from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.models import ContentType, CrawlLogStatus, Platform


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CreatorCreate(BaseModel):
    url: str
    note: str | None = None
    content_type: ContentType = ContentType.VIDEO


class CreatorUpdate(BaseModel):
    note: str | None = None
    category: str | None = None
    starred: bool | None = None
    content_type: ContentType | None = None


class CreatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform: Platform
    platform_creator_id: str
    name: str
    profile_url: str
    avatar_url: str | None
    note: str | None
    category: str | None
    content_type: ContentType
    starred: bool
    notifications_enabled: bool
    created_at: datetime


class VideoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    creator_id: str
    platform_video_id: str
    title: str
    thumbnail_url: str | None
    video_url: str
    published_at: datetime
    creator_name: str
    creator_avatar_url: str | None
    platform: Platform


class SettingsUpdate(BaseModel):
    feishu_webhook_url: str | None = None


class SettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    feishu_webhook_url: str | None
    created_at: datetime
    updated_at: datetime


class VideoListResponse(BaseModel):
    items: list["VideoResponse"]
    next_cursor: str | None
    has_more: bool


class FeishuWebhookCreate(BaseModel):
    name: str
    webhook_url: str


class FeishuWebhookUpdate(BaseModel):
    name: str | None = None
    enabled: bool | None = None


class FeishuWebhookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    webhook_url: str
    enabled: bool
    created_at: datetime


class CrawlAcceptedResponse(BaseModel):
    status: CrawlLogStatus
    videos_found: int


class CrawlLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    creator_id: str
    status: CrawlLogStatus
    message: str | None
    videos_found: int
    created_at: datetime
