from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from app.api.videos import list_videos
from app.models.models import Creator, Platform, User, Video


async def _seed_user(db) -> User:
    user = User(
        email="integration@example.com",
        password_hash="hashed",
        display_name="Integration Tester",
    )
    db.add(user)
    await db.flush()
    return user


async def _seed_creator(db, user_id: str) -> Creator:
    creator = Creator(
        user_id=user_id,
        platform=Platform.BILIBILI,
        platform_creator_id="integration_uid",
        name="Integration Creator",
        profile_url="https://space.bilibili.com/integration_uid",
    )
    db.add(creator)
    await db.flush()
    return creator


async def _seed_videos(db, creator: Creator, count: int) -> None:
    base = datetime(2024, 1, 1, tzinfo=UTC)
    for index in range(count):
        db.add(
            Video(
                creator_id=creator.id,
                platform_video_id=f"BV{index}",
                title=f"Video {index}",
                video_url=f"https://www.bilibili.com/video/BV{index}",
                published_at=base + timedelta(hours=index),
            )
        )
    await db.commit()


class TestVideosModuleIntegration:
    async def test_list_videos_paginates_with_cursor_directly(self, db):
        user = await _seed_user(db)
        creator = await _seed_creator(db, user.id)
        await _seed_videos(db, creator, 6)

        first_page = await list_videos(platform=None, cursor=None, limit=3, current_user=user, db=db)
        second_page = await list_videos(
            platform=None,
            cursor=first_page.next_cursor,
            limit=3,
            current_user=user,
            db=db,
        )

        first_ids = {item.id for item in first_page.items}
        second_ids = {item.id for item in second_page.items}

        assert len(first_page.items) == 3
        assert len(second_page.items) == 3
        assert first_ids.isdisjoint(second_ids)
        assert second_page.has_more is False

    async def test_list_videos_raises_400_for_invalid_cursor_directly(self, db):
        user = await _seed_user(db)

        with pytest.raises(HTTPException) as exc_info:
            await list_videos(platform=None, cursor="invalid", limit=3, current_user=user, db=db)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid cursor"
