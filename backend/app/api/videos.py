import base64
import binascii
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Platform, User, Video
from app.schemas.schemas import VideoListResponse, VideoResponse

router = APIRouter()

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


def _encode_cursor(published_at: str, video_id: str) -> str:
    payload = json.dumps({"published_at": published_at, "id": video_id})
    return base64.urlsafe_b64encode(payload.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[str, str]:
    payload = json.loads(base64.urlsafe_b64decode(cursor.encode()))
    return payload["published_at"], payload["id"]


@router.get("", response_model=VideoListResponse)
async def list_videos(
    platform: Platform | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VideoListResponse:
    stmt = (
        select(Video)
        .options(selectinload(Video.creator))
        .join(Video.creator)
        .where(Video.creator.has(user_id=current_user.id))
        .order_by(Video.published_at.desc(), Video.id.desc())
        .limit(limit + 1)
    )
    if platform is not None:
        stmt = stmt.where(Video.creator.has(platform=platform))
    if cursor is not None:
        try:
            cursor_published_at, cursor_id = _decode_cursor(cursor)
            cursor_dt = datetime.fromisoformat(cursor_published_at)
        except (binascii.Error, json.JSONDecodeError, KeyError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc
        stmt = stmt.where(
            or_(
                Video.published_at < cursor_dt,
                and_(Video.published_at == cursor_dt, Video.id < cursor_id),
            )
        )

    result = await db.scalars(stmt)
    videos = list(result)

    has_more = len(videos) > limit
    page = videos[:limit]

    next_cursor = None
    if has_more and page:
        last = page[-1]
        next_cursor = _encode_cursor(last.published_at.isoformat(), last.id)

    items = [
        VideoResponse(
            id=v.id,
            creator_id=v.creator_id,
            platform_video_id=v.platform_video_id,
            title=v.title,
            thumbnail_url=v.thumbnail_url,
            video_url=v.video_url,
            published_at=v.published_at,
            creator_name=v.creator.name,
            creator_avatar_url=v.creator.avatar_url,
            platform=v.creator.platform,
        )
        for v in page
    ]

    return VideoListResponse(items=items, next_cursor=next_cursor, has_more=has_more)
