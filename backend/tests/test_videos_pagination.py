"""
TDD: 视频流 API — 游标分页 + 状态更新
Round 1: GET /api/videos 返回分页结构 {items, next_cursor, has_more}，支持 limit
"""
from datetime import UTC, datetime, timedelta

import pytest

from app.models.models import Creator, Platform, Video


# ── seed helpers ──────────────────────────────────────────────────────────────

async def _seed_creator(db, user_id: str, suffix: str = "1") -> Creator:
    creator = Creator(
        user_id=user_id,
        platform=Platform.BILIBILI,
        platform_creator_id=f"uid_{suffix}",
        name=f"Creator {suffix}",
        profile_url=f"https://space.bilibili.com/{suffix}",
    )
    db.add(creator)
    await db.flush()
    return creator


async def _seed_videos(db, creator: Creator, n: int, base_dt: datetime | None = None) -> list[Video]:
    base = base_dt or datetime(2024, 1, 1, tzinfo=UTC)
    videos = []
    for i in range(n):
        v = Video(
            creator_id=creator.id,
            platform_video_id=f"BV{creator.platform_creator_id}_{i}",
            title=f"Video {i}",
            video_url=f"https://www.bilibili.com/video/BV{i}",
            published_at=base + timedelta(hours=i),
        )
        db.add(v)
        videos.append(v)
    await db.commit()
    return videos


# ── Round 1: 分页响应结构 ─────────────────────────────────────────────────────

class TestVideosPaginatedResponse:
    async def test_response_has_items_key(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 3)

        resp = await client.get("/api/videos", headers=auth_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()

    async def test_response_has_next_cursor_key(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 3)

        resp = await client.get("/api/videos", headers=auth_headers)
        assert "next_cursor" in resp.json()

    async def test_response_has_has_more_key(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 3)

        resp = await client.get("/api/videos", headers=auth_headers)
        assert "has_more" in resp.json()

    async def test_items_contain_video_fields(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 1)

        resp = await client.get("/api/videos", headers=auth_headers)
        item = resp.json()["items"][0]
        assert "id" in item
        assert "title" in item
        assert "video_url" in item
        assert "published_at" in item
        assert "creator_name" in item

    async def test_limit_param_restricts_items(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 10)

        resp = await client.get("/api/videos?limit=3", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 3

    async def test_has_more_true_when_more_exist(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 5)

        resp = await client.get("/api/videos?limit=3", headers=auth_headers)
        assert resp.json()["has_more"] is True

    async def test_has_more_false_when_all_returned(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 3)

        resp = await client.get("/api/videos?limit=10", headers=auth_headers)
        assert resp.json()["has_more"] is False

    async def test_next_cursor_is_none_when_no_more(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 2)

        resp = await client.get("/api/videos?limit=10", headers=auth_headers)
        assert resp.json()["next_cursor"] is None

    async def test_next_cursor_is_string_when_has_more(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 5)

        resp = await client.get("/api/videos?limit=3", headers=auth_headers)
        assert isinstance(resp.json()["next_cursor"], str)

    async def test_empty_db_returns_empty_items(self, client, auth_headers):
        resp = await client.get("/api/videos", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["items"] == []
        assert resp.json()["has_more"] is False
        assert resp.json()["next_cursor"] is None

    async def test_requires_auth(self, client):
        resp = await client.get("/api/videos")
        assert resp.status_code == 401


# ── Round 2: cursor 翻页 ──────────────────────────────────────────────────────

class TestVideosCursorPagination:
    async def test_second_page_has_no_overlap_with_first(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 6)

        r1 = await client.get("/api/videos?limit=3", headers=auth_headers)
        cursor = r1.json()["next_cursor"]
        r2 = await client.get(f"/api/videos?limit=3&cursor={cursor}", headers=auth_headers)

        ids1 = {v["id"] for v in r1.json()["items"]}
        ids2 = {v["id"] for v in r2.json()["items"]}
        assert ids1.isdisjoint(ids2)

    async def test_cursor_traversal_covers_all_videos(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 7)

        all_ids: set[str] = set()
        cursor = None
        while True:
            url = "/api/videos?limit=3"
            if cursor:
                url += f"&cursor={cursor}"
            resp = await client.get(url, headers=auth_headers)
            body = resp.json()
            all_ids.update(v["id"] for v in body["items"])
            cursor = body["next_cursor"]
            if not body["has_more"]:
                break

        assert len(all_ids) == 7

    async def test_second_page_items_older_than_first(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 6)

        r1 = await client.get("/api/videos?limit=3", headers=auth_headers)
        cursor = r1.json()["next_cursor"]
        r2 = await client.get(f"/api/videos?limit=3&cursor={cursor}", headers=auth_headers)

        oldest_p1 = min(v["published_at"] for v in r1.json()["items"])
        newest_p2 = max(v["published_at"] for v in r2.json()["items"])
        assert newest_p2 <= oldest_p1

    async def test_invalid_cursor_returns_400(self, client, auth_headers):
        resp = await client.get("/api/videos?cursor=notvalidbase64!!", headers=auth_headers)
        assert resp.status_code == 400

    async def test_cursor_page_has_correct_has_more(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 4)

        r1 = await client.get("/api/videos?limit=3", headers=auth_headers)
        cursor = r1.json()["next_cursor"]
        r2 = await client.get(f"/api/videos?limit=3&cursor={cursor}", headers=auth_headers)

        assert r1.json()["has_more"] is True
        assert r2.json()["has_more"] is False

    async def test_last_page_next_cursor_is_none(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        await _seed_videos(db, creator, 4)

        r1 = await client.get("/api/videos?limit=3", headers=auth_headers)
        cursor = r1.json()["next_cursor"]
        r2 = await client.get(f"/api/videos?limit=3&cursor={cursor}", headers=auth_headers)

        assert r2.json()["next_cursor"] is None

    async def test_cursor_handles_same_published_at_without_duplicates(self, client, auth_headers, db):
        me = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me.json()["id"]
        creator = await _seed_creator(db, user_id)
        same_dt = datetime(2024, 1, 1, tzinfo=UTC)
        await _seed_videos(db, creator, 5, base_dt=same_dt)

        r1 = await client.get("/api/videos?limit=3", headers=auth_headers)
        cursor = r1.json()["next_cursor"]
        r2 = await client.get(f"/api/videos?limit=3&cursor={cursor}", headers=auth_headers)

        ids1 = {v["id"] for v in r1.json()["items"]}
        ids2 = {v["id"] for v in r2.json()["items"]}

        assert len(r1.json()["items"]) == 3
        assert len(r2.json()["items"]) == 2
        assert ids1.isdisjoint(ids2)
        assert r2.json()["has_more"] is False
        assert r2.json()["next_cursor"] is None
