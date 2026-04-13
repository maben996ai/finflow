from app.models.models import Platform
from app.services.crawlers.bilibili import BilibiliCrawler
from app.services.crawlers.youtube import YouTubeCrawler


class CrawlerRegistry:
    def __init__(self) -> None:
        self._crawlers = {
            Platform.BILIBILI: BilibiliCrawler(),
            Platform.YOUTUBE: YouTubeCrawler(),
        }

    def get(self, platform: Platform):
        return self._crawlers[platform]


crawler_registry = CrawlerRegistry()

