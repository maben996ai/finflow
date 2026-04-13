from datetime import UTC, datetime

from app.models.models import Platform
from app.services.crawlers.base import BaseCrawler, CrawledVideo


class BilibiliCrawler(BaseCrawler):
    platform = Platform.BILIBILI

    async def fetch_latest_videos(self, creator_id: str) -> list[CrawledVideo]:
        return [
            CrawledVideo(
                platform=self.platform,
                platform_video_id=f"{creator_id}-bootstrap-video",
                title=f"Bilibili bootstrap video for {creator_id}",
                video_url=f"https://www.bilibili.com/{creator_id}",
                published_at=datetime.now(UTC),
            )
        ]

