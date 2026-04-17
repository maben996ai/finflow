import respx
import pytest
from datetime import UTC, datetime
from httpx import Response

from app.services.crawlers.bilibili import BilibiliCrawler

crawler = BilibiliCrawler()

BILIBILI_USER_INFO_OK = {
    "code": 0,
    "data": {
        "mid": 123456,
        "name": "测试UP主",
        "face": "https://example.com/avatar.jpg",
    },
}

BILIBILI_VIDEO_LIST_OK = {
    "data": {
        "list": {
            "vlist": [
                {
                    "bvid": "BV1xx411c7mu",
                    "title": "测试视频标题",
                    "pic": "https://example.com/thumb.jpg",
                    "created": 1700000000,
                },
                {
                    "bvid": "BV2yy422d8nv",
                    "title": "另一个视频",
                    "pic": None,
                    "created": 1699000000,
                },
            ]
        }
    }
}


class TestBilibiliResolveCreator:
    @respx.mock
    async def test_resolve_space_url_returns_creator_info(self):
        respx.get("https://api.bilibili.com/x/space/acc/info").mock(
            return_value=Response(200, json=BILIBILI_USER_INFO_OK)
        )

        creator = await crawler.resolve_creator("https://space.bilibili.com/123456")

        assert creator.platform_id == "123456"
        assert creator.name == "测试UP主"
        assert creator.avatar_url == "https://example.com/avatar.jpg"
        assert creator.profile_url == "https://space.bilibili.com/123456"

    @respx.mock
    async def test_resolve_b23tv_follows_redirect(self):
        respx.get("https://b23.tv/abc123").mock(
            return_value=Response(
                302,
                headers={"location": "https://space.bilibili.com/123456"},
            )
        )
        # respx doesn't auto-follow, so mock the final redirected URL too
        respx.get("https://space.bilibili.com/123456").mock(
            return_value=Response(200, json={}, headers={})
        )
        respx.get("https://api.bilibili.com/x/space/acc/info").mock(
            return_value=Response(200, json=BILIBILI_USER_INFO_OK)
        )

        creator = await crawler.resolve_creator("https://b23.tv/abc123")
        assert creator.platform_id == "123456"

    @respx.mock
    async def test_api_error_code_raises_value_error(self):
        respx.get("https://api.bilibili.com/x/space/acc/info").mock(
            return_value=Response(200, json={"code": -404, "data": None})
        )

        with pytest.raises(ValueError, match="Failed to resolve Bilibili creator"):
            await crawler.resolve_creator("https://space.bilibili.com/999")

    @respx.mock
    async def test_unsupported_url_raises_value_error(self):
        # URL that doesn't match space.bilibili.com, BV id, or mid param
        with pytest.raises(ValueError, match="Unsupported Bilibili creator URL"):
            await crawler.resolve_creator("https://www.bilibili.com/")


class TestBibiliFetchLatestVideos:
    @respx.mock
    async def test_returns_list_of_crawled_videos(self):
        respx.get("https://api.bilibili.com/x/space/arc/search").mock(
            return_value=Response(200, json=BILIBILI_VIDEO_LIST_OK)
        )

        videos = await crawler.fetch_latest_videos("123456")

        assert len(videos) == 2
        assert videos[0].platform_video_id == "BV1xx411c7mu"
        assert videos[0].title == "测试视频标题"
        assert videos[0].video_url == "https://www.bilibili.com/video/BV1xx411c7mu"
        assert videos[0].thumbnail_url == "https://example.com/thumb.jpg"
        assert isinstance(videos[0].published_at, datetime)

    @respx.mock
    async def test_published_at_is_utc_aware(self):
        respx.get("https://api.bilibili.com/x/space/arc/search").mock(
            return_value=Response(200, json=BILIBILI_VIDEO_LIST_OK)
        )

        videos = await crawler.fetch_latest_videos("123456")
        assert videos[0].published_at.tzinfo == UTC

    @respx.mock
    async def test_empty_video_list_returns_empty(self):
        respx.get("https://api.bilibili.com/x/space/arc/search").mock(
            return_value=Response(200, json={"data": {"list": {"vlist": []}}})
        )

        videos = await crawler.fetch_latest_videos("123456")
        assert videos == []

    @respx.mock
    async def test_items_missing_bvid_are_skipped(self):
        respx.get("https://api.bilibili.com/x/space/arc/search").mock(
            return_value=Response(
                200,
                json={"data": {"list": {"vlist": [{"title": "no bvid", "created": 0}]}}},
            )
        )

        videos = await crawler.fetch_latest_videos("123456")
        assert videos == []
