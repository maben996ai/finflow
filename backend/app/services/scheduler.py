import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.models import CrawlLogStatus, Creator, CrawlLog, UserSettings, Video
from app.services.crawlers.registry import crawler_registry
from app.services.notifiers.feishu import FeishuNotifier

_notifier = FeishuNotifier()


class SchedulerService:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        self.scheduler.add_job(crawl_all_creators, "interval", minutes=30, id="crawl_all_creators", replace_existing=True)
        self.scheduler.start()
        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return
        self.scheduler.shutdown(wait=False)
        self._started = False


FIRST_CRAWL_LIMIT = 30
INCREMENTAL_CRAWL_LIMIT = 2


async def _get_webhook_url(user_id: str) -> str | None:
    async with AsyncSessionLocal() as db:
        settings = await db.scalar(select(UserSettings).where(UserSettings.user_id == user_id))
        return settings.feishu_webhook_url if settings else None


async def crawl_creator(creator: Creator) -> int:
    crawler = crawler_registry.get(creator.platform)

    async with AsyncSessionLocal() as db:
        existing_count = await db.scalar(
            select(func.count()).select_from(Video).where(Video.creator_id == creator.id)
        )

    is_first_crawl = (existing_count or 0) == 0
    limit = FIRST_CRAWL_LIMIT if is_first_crawl else INCREMENTAL_CRAWL_LIMIT

    videos = await crawler.fetch_latest_videos(creator.platform_creator_id, limit=limit)

    async with AsyncSessionLocal() as db:
        if not videos:
            db.add(CrawlLog(creator_id=creator.id, status=CrawlLogStatus.SUCCESS, message=None, videos_found=0))
            await db.commit()
            return 0

        fetched_ids = {v.platform_video_id for v in videos}
        existing_rows = {
            row.platform_video_id: row
            for row in await db.scalars(
                select(Video).where(
                    Video.creator_id == creator.id,
                    Video.platform_video_id.in_(fetched_ids),
                )
            )
        }

        inserted_videos: list[Video] = []
        for video in videos:
            if video.platform_video_id in existing_rows:
                row = existing_rows[video.platform_video_id]
                row.title = video.title
                row.thumbnail_url = video.thumbnail_url
                row.video_url = video.video_url
                row.raw_data = video.raw_data
            else:
                new_video = Video(
                    creator_id=creator.id,
                    platform_video_id=video.platform_video_id,
                    title=video.title,
                    thumbnail_url=video.thumbnail_url,
                    video_url=video.video_url,
                    published_at=video.published_at,
                    raw_data=video.raw_data,
                )
                db.add(new_video)
                inserted_videos.append(new_video)

        db.add(
            CrawlLog(
                creator_id=creator.id,
                status=CrawlLogStatus.SUCCESS,
                message=None,
                videos_found=len(inserted_videos),
            )
        )
        await db.commit()

    # Send notifications after commit
    if creator.notifications_enabled and inserted_videos:
        webhook_url = await _get_webhook_url(creator.user_id)
        if webhook_url:
            if is_first_crawl:
                # First crawl: notify only the latest video (first in list), mark as new creator
                video_to_notify = inserted_videos[0]
                await _notifier.send_card(
                    webhook_url=webhook_url,
                    title=video_to_notify.title,
                    creator_name=creator.name,
                    platform=creator.platform,
                    video_url=video_to_notify.video_url,
                    is_new_creator=True,
                )
            else:
                # Incremental: notify all new videos
                for video in inserted_videos:
                    await _notifier.send_card(
                        webhook_url=webhook_url,
                        title=video.title,
                        creator_name=creator.name,
                        platform=creator.platform,
                        video_url=video.video_url,
                        is_new_creator=False,
                    )

    return len(inserted_videos)


async def crawl_all_creators() -> None:
    async with AsyncSessionLocal() as db:
        creators = list(await db.scalars(select(Creator)))

    results = await asyncio.gather(*[crawl_creator(c) for c in creators], return_exceptions=True)

    failed = [
        (creators[i], exc)
        for i, exc in enumerate(results)
        if isinstance(exc, Exception)
    ]
    if not failed:
        return

    async with AsyncSessionLocal() as db:
        for creator, exc in failed:
            db.add(
                CrawlLog(
                    creator_id=creator.id,
                    status=CrawlLogStatus.FAILED,
                    message=str(exc),
                    videos_found=0,
                )
            )
        await db.commit()


scheduler_service = SchedulerService()
