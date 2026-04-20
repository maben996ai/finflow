from app.models.models import SourceType
from app.services.crawlers.bilibili import BilibiliCrawler
from app.services.crawlers.youtube import YouTubeCrawler


class CrawlerRegistry:
    def __init__(self) -> None:
        self._crawlers = {
            SourceType.BILIBILI: BilibiliCrawler(),
            SourceType.YOUTUBE: YouTubeCrawler(),
        }

    def get(self, source_type: SourceType):
        return self._crawlers[source_type]


crawler_registry = CrawlerRegistry()
