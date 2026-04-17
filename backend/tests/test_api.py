from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.models.models import CrawlLog, CrawlLogStatus, Creator, Platform, Video
from app.services.crawlers.base import CreatorInfo


# ── helpers ──────────────────────────────────────────────────────────────────

REGISTER_PAYLOAD = {
    "email": "alice@example.com",
    "password": "password123",
    "display_name": "Alice",
}

MOCK_CREATOR_INFO = CreatorInfo(
    platform_id="123456",
    name="测试UP主",
    profile_url="https://space.bilibili.com/123456",
    avatar_url=None,
)


# ── auth ─────────────────────────────────────────────────────────────────────

class TestAuthRegister:
    async def test_register_returns_201_and_user_fields(self, client):
        resp = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "alice@example.com"
        assert body["display_name"] == "Alice"
        assert "id" in body

    async def test_register_duplicate_email_returns_409(self, client):
        await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
        resp = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
        assert resp.status_code == 409

    async def test_register_uses_email_prefix_as_display_name_when_omitted(self, client):
        payload = {"email": "bob@example.com", "password": "password123"}
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        assert resp.json()["display_name"] == "bob"

    async def test_register_short_password_returns_422(self, client):
        payload = {**REGISTER_PAYLOAD, "password": "short"}
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 422


class TestAuthLogin:
    async def test_login_returns_access_token(self, client):
        await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
        resp = await client.post(
            "/api/auth/login",
            json={"email": "alice@example.com", "password": "password123"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_wrong_password_returns_401(self, client):
        await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
        resp = await client.post(
            "/api/auth/login",
            json={"email": "alice@example.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    async def test_login_unknown_email_returns_401(self, client):
        resp = await client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "password123"},
        )
        assert resp.status_code == 401


class TestAuthMe:
    async def test_me_returns_current_user(self, client, auth_headers):
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    async def test_me_without_token_returns_401(self, client):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401


# ── creators ─────────────────────────────────────────────────────────────────

class TestCreatorsAPI:
    async def test_list_creators_empty_for_new_user(self, client, auth_headers):
        resp = await client.get("/api/creators", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_create_creator_returns_201(self, client, auth_headers):
        with patch(
            "app.api.creators.resolve_creator",
            new=AsyncMock(return_value=(Platform.BILIBILI, MOCK_CREATOR_INFO)),
        ):
            resp = await client.post(
                "/api/creators",
                json={"url": "https://space.bilibili.com/123456"},
                headers=auth_headers,
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "测试UP主"
        assert body["platform"] == "bilibili"
        assert body["platform_creator_id"] == "123456"

    async def test_create_duplicate_creator_returns_409(self, client, auth_headers):
        with patch(
            "app.api.creators.resolve_creator",
            new=AsyncMock(return_value=(Platform.BILIBILI, MOCK_CREATOR_INFO)),
        ):
            await client.post(
                "/api/creators",
                json={"url": "https://space.bilibili.com/123456"},
                headers=auth_headers,
            )
            resp = await client.post(
                "/api/creators",
                json={"url": "https://space.bilibili.com/123456"},
                headers=auth_headers,
            )
        assert resp.status_code == 409

    async def test_create_creator_unsupported_url_returns_400(self, client, auth_headers):
        with patch(
            "app.api.creators.resolve_creator",
            new=AsyncMock(side_effect=ValueError("Unsupported creator URL")),
        ):
            resp = await client.post(
                "/api/creators",
                json={"url": "https://twitter.com/someone"},
                headers=auth_headers,
            )
        assert resp.status_code == 400

    async def test_delete_creator_returns_204(self, client, auth_headers, db):
        with patch(
            "app.api.creators.resolve_creator",
            new=AsyncMock(return_value=(Platform.BILIBILI, MOCK_CREATOR_INFO)),
        ):
            create_resp = await client.post(
                "/api/creators",
                json={"url": "https://space.bilibili.com/123456"},
                headers=auth_headers,
            )
        creator_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/creators/{creator_id}", headers=auth_headers)
        assert resp.status_code == 204

    async def test_delete_nonexistent_creator_returns_404(self, client, auth_headers):
        resp = await client.delete("/api/creators/nonexistent-id", headers=auth_headers)
        assert resp.status_code == 404

    async def test_trigger_crawl_returns_success(self, client, auth_headers, db):
        with patch(
            "app.api.creators.resolve_creator",
            new=AsyncMock(return_value=(Platform.BILIBILI, MOCK_CREATOR_INFO)),
        ):
            create_resp = await client.post(
                "/api/creators",
                json={"url": "https://space.bilibili.com/123456"},
                headers=auth_headers,
            )
        creator_id = create_resp.json()["id"]

        with patch("app.api.creators.crawl_creator", new=AsyncMock(return_value=3)):
            resp = await client.post(f"/api/creators/{creator_id}/crawl", headers=auth_headers)

        assert resp.status_code == 200
        assert resp.json()["videos_found"] == 3
        assert resp.json()["status"] == "success"


# ── videos ───────────────────────────────────────────────────────────────────

class TestVideosAPI:
    async def _seed_video(self, db, user_id: str) -> Video:
        creator = Creator(
            user_id=user_id,
            platform=Platform.BILIBILI,
            platform_creator_id="111",
            name="Seeded Creator",
            profile_url="https://space.bilibili.com/111",
        )
        db.add(creator)
        await db.flush()
        video = Video(
            creator_id=creator.id,
            platform_video_id="BVtest",
            title="Test Video",
            video_url="https://www.bilibili.com/video/BVtest",
            published_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        db.add(video)
        await db.commit()
        return video

    async def test_list_videos_returns_user_videos(self, client, auth_headers, db):
        me_resp = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me_resp.json()["id"]
        await self._seed_video(db, user_id)

        resp = await client.get("/api/videos", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["title"] == "Test Video"

    async def test_list_videos_filter_by_platform(self, client, auth_headers, db):
        me_resp = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me_resp.json()["id"]
        await self._seed_video(db, user_id)

        resp = await client.get("/api/videos?platform=youtube", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_videos_requires_auth(self, client):
        resp = await client.get("/api/videos")
        assert resp.status_code == 401


# ── settings ─────────────────────────────────────────────────────────────────

class TestSettingsAPI:
    async def test_get_feishu_settings_returns_defaults(self, client, auth_headers):
        resp = await client.get("/api/settings/feishu", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["feishu_webhook_url"] is None

    async def test_update_feishu_webhook(self, client, auth_headers):
        resp = await client.put(
            "/api/settings/feishu",
            json={"feishu_webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["feishu_webhook_url"] == "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"

    async def test_update_then_get_reflects_change(self, client, auth_headers):
        await client.put(
            "/api/settings/feishu",
            json={"feishu_webhook_url": "https://example.com/webhook"},
            headers=auth_headers,
        )
        resp = await client.get("/api/settings/feishu", headers=auth_headers)
        assert resp.json()["feishu_webhook_url"] == "https://example.com/webhook"


# ── crawl logs ────────────────────────────────────────────────────────────────

class TestCrawlLogsAPI:
    async def _seed_log(
        self, db, user_id: str, status: CrawlLogStatus, platform_creator_id: str = "999"
    ) -> CrawlLog:
        creator = Creator(
            user_id=user_id,
            platform=Platform.BILIBILI,
            platform_creator_id=platform_creator_id,
            name="Log Creator",
            profile_url=f"https://space.bilibili.com/{platform_creator_id}",
        )
        db.add(creator)
        await db.flush()
        log = CrawlLog(creator_id=creator.id, status=status, videos_found=1)
        db.add(log)
        await db.commit()
        return log

    async def test_list_crawl_logs_returns_user_logs(self, client, auth_headers, db):
        me_resp = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me_resp.json()["id"]
        await self._seed_log(db, user_id, CrawlLogStatus.SUCCESS)

        resp = await client.get("/api/crawl-logs", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_filter_by_status(self, client, auth_headers, db):
        me_resp = await client.get("/api/auth/me", headers=auth_headers)
        user_id = me_resp.json()["id"]
        await self._seed_log(db, user_id, CrawlLogStatus.SUCCESS, platform_creator_id="998")
        await self._seed_log(db, user_id, CrawlLogStatus.FAILED, platform_creator_id="999")

        resp = await client.get("/api/crawl-logs?status=failed", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["status"] == "failed"

    async def test_requires_auth(self, client):
        resp = await client.get("/api/crawl-logs")
        assert resp.status_code == 401
