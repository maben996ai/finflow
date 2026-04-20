from unittest.mock import AsyncMock, patch

import pytest

from app.models.models import SourceType
from app.services.crawlers.base import SourceInfo
from app.services.resolver import resolve_source

MOCK_BILIBILI_SOURCE = SourceInfo(
    platform_id="123456",
    name="测试UP主",
    profile_url="https://space.bilibili.com/123456",
    avatar_url=None,
)

MOCK_YOUTUBE_SOURCE = SourceInfo(
    platform_id="UCxxxx",
    name="Test Channel",
    profile_url="https://www.youtube.com/@testchannel",
    avatar_url=None,
)


def make_mock_crawler(source_info: SourceInfo) -> AsyncMock:
    crawler = AsyncMock()
    crawler.resolve_source = AsyncMock(return_value=source_info)
    return crawler


class TestResolverPatternMatching:
    @pytest.mark.parametrize(
        "url",
        [
            "https://space.bilibili.com/123456",
            "https://space.bilibili.com/99999999",
            "https://b23.tv/abc123",
        ],
    )
    async def test_bilibili_urls_resolve_to_bilibili_source_type(self, url):
        with patch(
            "app.services.resolver.crawler_registry.get",
            return_value=make_mock_crawler(MOCK_BILIBILI_SOURCE),
        ):
            source_type, _ = await resolve_source(url)
        assert source_type == SourceType.BILIBILI

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/channel/UCxxxxxx",
            "https://youtube.com/channel/UCxxxxxx",
            "https://www.youtube.com/@testchannel",
            "https://youtube.com/@testchannel",
        ],
    )
    async def test_youtube_urls_resolve_to_youtube_source_type(self, url):
        with patch(
            "app.services.resolver.crawler_registry.get",
            return_value=make_mock_crawler(MOCK_YOUTUBE_SOURCE),
        ):
            source_type, _ = await resolve_source(url)
        assert source_type == SourceType.YOUTUBE

    async def test_unsupported_url_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported source URL"):
            await resolve_source("https://twitter.com/someone")

    async def test_url_with_leading_spaces_is_normalized(self):
        with patch(
            "app.services.resolver.crawler_registry.get",
            return_value=make_mock_crawler(MOCK_BILIBILI_SOURCE),
        ):
            source_type, _ = await resolve_source("  https://space.bilibili.com/123456  ")
        assert source_type == SourceType.BILIBILI

    async def test_returns_source_info_from_crawler(self):
        with patch(
            "app.services.resolver.crawler_registry.get",
            return_value=make_mock_crawler(MOCK_BILIBILI_SOURCE),
        ):
            _, source = await resolve_source("https://space.bilibili.com/123456")
        assert source.platform_id == "123456"
        assert source.name == "测试UP主"
