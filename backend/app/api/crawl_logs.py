from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import CrawlLog, User
from app.schemas.schemas import CrawlLogResponse

router = APIRouter()


@router.get("", response_model=list[CrawlLogResponse])
async def list_crawl_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CrawlLog]:
    result = await db.scalars(
        select(CrawlLog)
        .options(selectinload(CrawlLog.creator))
        .join(CrawlLog.creator)
        .where(CrawlLog.creator.has(user_id=current_user.id))
        .order_by(CrawlLog.created_at.desc())
    )
    return list(result)

