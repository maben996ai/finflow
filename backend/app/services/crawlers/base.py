from dataclasses import dataclass
from datetime import datetime

from app.models.models import Platform


@dataclass
class CrawledVideo:
    platform: Platform
    platform_video_id: str
    title: str
    video_url: str
    published_at: datetime
    thumbnail_url: str | None = None


class BaseCrawler:
    platform: Platform

    async def fetch_latest_videos(self, creator_id: str) -> list[CrawledVideo]:
        raise NotImplementedError

