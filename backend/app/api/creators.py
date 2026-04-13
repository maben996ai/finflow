from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Creator, User
from app.schemas.schemas import CreatorCreate, CreatorResponse
from app.services.resolver import resolve_creator

router = APIRouter()


@router.get("", response_model=list[CreatorResponse])
async def list_creators(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Creator]:
    result = await db.scalars(
        select(Creator)
        .where(Creator.user_id == current_user.id)
        .order_by(Creator.created_at.desc())
    )
    return list(result)


@router.post("", response_model=CreatorResponse, status_code=status.HTTP_201_CREATED)
async def create_creator(
    payload: CreatorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Creator:
    try:
        resolved = resolve_creator(payload.url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    existing_creator = await db.scalar(
        select(Creator).where(
            Creator.user_id == current_user.id,
            Creator.platform == resolved.platform,
            Creator.platform_creator_id == resolved.platform_creator_id,
        )
    )
    if existing_creator is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Creator already exists",
        )

    creator = Creator(
        user_id=current_user.id,
        platform=resolved.platform,
        platform_creator_id=resolved.platform_creator_id,
        name=resolved.name,
        profile_url=payload.url,
        avatar_url=resolved.avatar_url,
        note=payload.note,
    )
    db.add(creator)
    await db.commit()
    await db.refresh(creator)
    return creator


@router.delete("/{creator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creator(
    creator_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    creator = await db.scalar(
        select(Creator).where(
            Creator.id == creator_id,
            Creator.user_id == current_user.id,
        )
    )
    if creator is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

    await db.delete(creator)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
