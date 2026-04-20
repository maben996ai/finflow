import base64
import binascii
import json
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import SourceType, User, Video
from app.schemas.schemas import VideoListResponse, VideoResponse

router = APIRouter()

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


def _parse_hms_duration(value: str) -> int | None:
    parts = value.strip().split(":")
    if not 2 <= len(parts) <= 3 or not all(part.isdigit() for part in parts):
        return None
    numbers = [int(part) for part in parts]
    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds
    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


def _parse_iso8601_duration(value: str) -> int | None:
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value)
    if not match:
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def _extract_duration_seconds(raw_data: dict | None) -> int | None:
    if not raw_data:
        return None

    candidates = [
        raw_data.get("duration"),
        raw_data.get("length"),
        raw_data.get("duration_seconds"),
        raw_data.get("lengthSeconds"),
        (raw_data.get("contentDetails") or {}).get("duration"),
    ]
    for value in candidates:
        if value is None:
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            if value.isdigit():
                return int(value)
            parsed = _parse_hms_duration(value)
            if parsed is not None:
                return parsed
            parsed = _parse_iso8601_duration(value)
            if parsed is not None:
                return parsed
    return None


def _encode_cursor(published_at: str, video_id: str) -> str:
    payload = json.dumps({"published_at": published_at, "id": video_id})
    return base64.urlsafe_b64encode(payload.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[str, str]:
    payload = json.loads(base64.urlsafe_b64decode(cursor.encode()))
    return payload["published_at"], payload["id"]


@router.get("", response_model=VideoListResponse)
async def list_videos(
    source_type: SourceType | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VideoListResponse:
    stmt = (
        select(Video)
        .options(selectinload(Video.data_source))
        .join(Video.data_source)
        .where(Video.data_source.has(user_id=current_user.id))
        .order_by(Video.published_at.desc(), Video.id.desc())
        .limit(limit + 1)
    )
    if source_type is not None:
        stmt = stmt.where(Video.data_source.has(source_type=source_type))
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
            data_source_id=v.data_source_id,
            platform_video_id=v.platform_video_id,
            title=v.title,
            thumbnail_url=v.thumbnail_url,
            video_url=v.video_url,
            published_at=v.published_at,
            duration_seconds=_extract_duration_seconds(v.raw_data),
            data_source_name=v.data_source.name,
            data_source_avatar_url=v.data_source.avatar_url,
            source_type=v.data_source.source_type,
        )
        for v in page
    ]

    return VideoListResponse(items=items, next_cursor=next_cursor, has_more=has_more)
