from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import User, Video
from app.schemas.schemas import VideoResponse

router = APIRouter()


@router.get("", response_model=list[VideoResponse])
async def list_videos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Video]:
    result = await db.scalars(
        select(Video)
        .options(selectinload(Video.creator))
        .join(Video.creator)
        .where(Video.creator.has(user_id=current_user.id))
        .order_by(Video.published_at.desc())
    )
    return list(result)

