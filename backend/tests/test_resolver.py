from unittest.mock import AsyncMock, patch

import pytest

from app.models.models import Platform
from app.services.crawlers.base import CreatorInfo
from app.services.resolver import resolve_creator

MOCK_BILIBILI_CREATOR = CreatorInfo(
    platform_id="123456",
    name="测试UP主",
    profile_url="https://space.bilibili.com/123456",
    avatar_url=None,
)

MOCK_YOUTUBE_CREATOR = CreatorInfo(
    platform_id="UCxxxx",
    name="Test Channel",
    profile_url="https://www.youtube.com/@testchannel",
    avatar_url=None,
)


def make_mock_crawler(creator_info: CreatorInfo) -> AsyncMock:
    crawler = AsyncMock()
    crawler.resolve_creator = AsyncMock(return_value=creator_info)
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
    async def test_bilibili_urls_resolve_to_bilibili_platform(self, url):
        with patch(
            "app.services.resolver.crawler_registry.get",
            return_value=make_mock_crawler(MOCK_BILIBILI_CREATOR),
        ):
            platform, _ = await resolve_creator(url)
        assert platform == Platform.BILIBILI

    @pytest.mark.parametrize(
        "url",
        [
            "https://www.youtube.com/channel/UCxxxxxx",
            "https://youtube.com/channel/UCxxxxxx",
            "https://www.youtube.com/@testchannel",
            "https://youtube.com/@testchannel",
        ],
    )
    async def test_youtube_urls_resolve_to_youtube_platform(self, url):
        with patch(
            "app.services.resolver.crawler_registry.get",
            return_value=make_mock_crawler(MOCK_YOUTUBE_CREATOR),
        ):
            platform, _ = await resolve_creator(url)
        assert platform == Platform.YOUTUBE

    async def test_unsupported_url_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported creator URL"):
            await resolve_creator("https://twitter.com/someone")

    async def test_url_with_leading_spaces_is_normalized(self):
        with patch(
            "app.services.resolver.crawler_registry.get",
            return_value=make_mock_crawler(MOCK_BILIBILI_CREATOR),
        ):
            platform, _ = await resolve_creator("  https://space.bilibili.com/123456  ")
        assert platform == Platform.BILIBILI

    async def test_returns_creator_info_from_crawler(self):
        with patch(
            "app.services.resolver.crawler_registry.get",
            return_value=make_mock_crawler(MOCK_BILIBILI_CREATOR),
        ):
            _, creator = await resolve_creator("https://space.bilibili.com/123456")
        assert creator.platform_id == "123456"
        assert creator.name == "测试UP主"
