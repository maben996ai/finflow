from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import CrawlLog, CrawlLogStatus, User
from app.schemas.schemas import CrawlLogResponse

router = APIRouter()


@router.get("", response_model=list[CrawlLogResponse])
async def list_crawl_logs(
    status: CrawlLogStatus | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CrawlLog]:
    stmt = (
        select(CrawlLog)
        .options(selectinload(CrawlLog.data_source))
        .join(CrawlLog.data_source)
        .where(CrawlLog.data_source.has(user_id=current_user.id))
        .order_by(CrawlLog.created_at.desc())
    )
    if status is not None:
        stmt = stmt.where(CrawlLog.status == status)
    stmt = stmt.limit(limit)

    result = await db.scalars(stmt)
    return list(result)
