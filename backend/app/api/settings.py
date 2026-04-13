from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import User, UserSettings
from app.schemas.schemas import SettingsResponse, SettingsUpdate

router = APIRouter()


@router.get("/feishu", response_model=SettingsResponse)
async def get_feishu_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettings:
    settings = await db.scalar(select(UserSettings).where(UserSettings.user_id == current_user.id))
    return settings


@router.put("/feishu", response_model=SettingsResponse)
async def update_feishu_settings(
    payload: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettings:
    settings = await db.scalar(select(UserSettings).where(UserSettings.user_id == current_user.id))
    settings.feishu_webhook_url = payload.feishu_webhook_url
    await db.commit()
    await db.refresh(settings)
    return settings

