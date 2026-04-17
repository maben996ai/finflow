from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.models import CrawlLog, CrawlLogStatus, Creator, Platform, User, Video
from app.services.crawlers.base import CrawledVideo
from app.services.scheduler import SchedulerService, crawl_all_creators, crawl_creator


def make_user() -> User:
    return User(email="test@example.com", password_hash="x", display_name="Tester")


def make_creator(user_id: str, platform: Platform = Platform.BILIBILI) -> Creator:
    return Creator(
        user_id=user_id,
        platform=platform,
        platform_creator_id="123456",
        name="Test Creator",
        profile_url="https://space.bilibili.com/123456",
    )


def make_video(platform_video_id: str = "BV001") -> CrawledVideo:
    return CrawledVideo(
        platform_video_id=platform_video_id,
        title="Test Video",
        video_url=f"https://www.bilibili.com/video/{platform_video_id}",
        published_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class TestSchedulerService:
    async def test_start_is_idempotent(self):
        svc = SchedulerService()
        with patch.object(svc.scheduler, "start") as mock_start, patch.object(
            svc.scheduler, "add_job"
        ):
            await svc.start()
            await svc.start()
        mock_start.assert_called_once()

    async def test_stop_is_idempotent(self):
        svc = SchedulerService()
        with patch.object(svc.scheduler, "start"), patch.object(svc.scheduler, "add_job"):
            await svc.start()

        with patch.object(svc.scheduler, "shutdown") as mock_shutdown:
            await svc.stop()
            await svc.stop()
        mock_shutdown.assert_called_once()

    async def test_stop_before_start_does_nothing(self):
        svc = SchedulerService()
        with patch.object(svc.scheduler, "shutdown") as mock_shutdown:
            await svc.stop()
        mock_shutdown.assert_not_called()


class TestCrawlCreator:
    async def test_new_videos_are_inserted(self, db, session_factory):
        user = make_user()
        db.add(user)
        await db.flush()
        creator = make_creator(user.id)
        db.add(creator)
        await db.commit()

        mock_crawler = AsyncMock()
        mock_crawler.fetch_latest_videos = AsyncMock(return_value=[make_video("BV001")])

        with (
            patch("app.services.scheduler.crawler_registry") as mock_registry,
            patch("app.services.scheduler.AsyncSessionLocal", session_factory),
        ):
            mock_registry.get.return_value = mock_crawler
            inserted = await crawl_creator(creator)

        assert inserted == 1
        async with session_factory() as s:
            videos = list(await s.scalars(select(Video).where(Video.creator_id == creator.id)))
        assert len(videos) == 1
        assert videos[0].platform_video_id == "BV001"

    async def test_duplicate_videos_are_not_reinserted(self, db, session_factory):
        user = make_user()
        db.add(user)
        await db.flush()
        creator = make_creator(user.id)
        db.add(creator)
        await db.flush()
        existing = Video(
            creator_id=creator.id,
            platform_video_id="BV001",
            title="Existing",
            video_url="https://www.bilibili.com/video/BV001",
            published_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        db.add(existing)
        await db.commit()

        mock_crawler = AsyncMock()
        mock_crawler.fetch_latest_videos = AsyncMock(return_value=[make_video("BV001")])

        with (
            patch("app.services.scheduler.crawler_registry") as mock_registry,
            patch("app.services.scheduler.AsyncSessionLocal", session_factory),
        ):
            mock_registry.get.return_value = mock_crawler
            inserted = await crawl_creator(creator)

        assert inserted == 0

    async def test_crawl_log_is_created_on_success(self, db, session_factory):
        user = make_user()
        db.add(user)
        await db.flush()
        creator = make_creator(user.id)
        db.add(creator)
        await db.commit()

        mock_crawler = AsyncMock()
        mock_crawler.fetch_latest_videos = AsyncMock(return_value=[make_video("BV001")])

        with (
            patch("app.services.scheduler.crawler_registry") as mock_registry,
            patch("app.services.scheduler.AsyncSessionLocal", session_factory),
        ):
            mock_registry.get.return_value = mock_crawler
            await crawl_creator(creator)

        async with session_factory() as s:
            log = await s.scalar(select(CrawlLog).where(CrawlLog.creator_id == creator.id))
        assert log is not None
        assert log.status == CrawlLogStatus.SUCCESS
        assert log.videos_found == 1

    async def test_empty_crawl_creates_log_with_zero_videos(self, db, session_factory):
        user = make_user()
        db.add(user)
        await db.flush()
        creator = make_creator(user.id)
        db.add(creator)
        await db.commit()

        mock_crawler = AsyncMock()
        mock_crawler.fetch_latest_videos = AsyncMock(return_value=[])

        with (
            patch("app.services.scheduler.crawler_registry") as mock_registry,
            patch("app.services.scheduler.AsyncSessionLocal", session_factory),
        ):
            mock_registry.get.return_value = mock_crawler
            inserted = await crawl_creator(creator)

        assert inserted == 0
        async with session_factory() as s:
            log = await s.scalar(select(CrawlLog).where(CrawlLog.creator_id == creator.id))
        assert log.videos_found == 0


class TestCrawlAllCreators:
    async def test_failed_crawl_writes_failed_log(self, db, session_factory):
        user = make_user()
        db.add(user)
        await db.flush()
        creator = make_creator(user.id)
        db.add(creator)
        await db.commit()

        async def _fake_crawl_creator(c):
            raise RuntimeError("API timeout")

        with (
            patch("app.services.scheduler.AsyncSessionLocal", session_factory),
            patch("app.services.scheduler.crawl_creator", side_effect=_fake_crawl_creator),
        ):
            await crawl_all_creators()

        async with session_factory() as s:
            log = await s.scalar(select(CrawlLog).where(CrawlLog.creator_id == creator.id))
        assert log.status == CrawlLogStatus.FAILED
        assert "API timeout" in log.message
