from unittest.mock import patch

import pytest
import respx
from httpx import Response

from app.services.crawlers.youtube import YouTubeCrawler

crawler = YouTubeCrawler()

YOUTUBE_CHANNEL_OK = {
    "items": [
        {
            "id": "UCxxxxxx",
            "snippet": {
                "title": "Test Channel",
                "thumbnails": {"high": {"url": "https://example.com/avatar.jpg"}},
            },
        }
    ]
}

YOUTUBE_HANDLE_ID_OK = {"items": [{"id": "UCxxxxxx"}]}

YOUTUBE_SEARCH_OK = {
    "items": [
        {
            "id": {"videoId": "vid001"},
            "snippet": {
                "title": "Video One",
                "publishedAt": "2024-01-15T10:00:00Z",
                "thumbnails": {"high": {"url": "https://example.com/thumb1.jpg"}},
            },
        },
        {
            "id": {"videoId": "vid002"},
            "snippet": {
                "title": "Video Two",
                "publishedAt": "2024-01-10T08:00:00Z",
                "thumbnails": {},
            },
        },
    ]
}


def _with_api_key(settings_override):
    settings_override.youtube_api_key = "fake-api-key"
    return settings_override


class TestYouTubeResolveCreator:
    @respx.mock
    async def test_resolve_channel_url_returns_creator_info(self):
        respx.get("https://www.googleapis.com/youtube/v3/channels").mock(
            return_value=Response(200, json=YOUTUBE_CHANNEL_OK)
        )

        with patch("app.services.crawlers.youtube.settings") as mock_settings:
            mock_settings.youtube_api_key = "fake-key"
            creator = await crawler.resolve_creator("https://www.youtube.com/channel/UCxxxxxx")

        assert creator.platform_id == "UCxxxxxx"
        assert creator.name == "Test Channel"
        assert creator.avatar_url == "https://example.com/avatar.jpg"
        assert creator.profile_url == "https://www.youtube.com/channel/UCxxxxxx"

    @respx.mock
    async def test_resolve_handle_url_resolves_via_api(self):
        respx.get("https://www.googleapis.com/youtube/v3/channels").mock(
            side_effect=[
                Response(200, json=YOUTUBE_HANDLE_ID_OK),
                Response(200, json=YOUTUBE_CHANNEL_OK),
            ]
        )

        with patch("app.services.crawlers.youtube.settings") as mock_settings:
            mock_settings.youtube_api_key = "fake-key"
            creator = await crawler.resolve_creator("https://www.youtube.com/@testchannel")

        assert creator.platform_id == "UCxxxxxx"

    async def test_no_api_key_raises_value_error(self):
        with patch("app.services.crawlers.youtube.settings") as mock_settings:
            mock_settings.youtube_api_key = ""
            with pytest.raises(ValueError, match="YOUTUBE_API_KEY is required"):
                await crawler.resolve_creator("https://www.youtube.com/channel/UCxxxxxx")

    @respx.mock
    async def test_channel_not_found_raises_value_error(self):
        respx.get("https://www.googleapis.com/youtube/v3/channels").mock(
            return_value=Response(200, json={"items": []})
        )

        with patch("app.services.crawlers.youtube.settings") as mock_settings:
            mock_settings.youtube_api_key = "fake-key"
            with pytest.raises(ValueError, match="Failed to resolve YouTube creator"):
                await crawler.resolve_creator("https://www.youtube.com/channel/UCxxxxxx")


class TestYouTubeFetchLatestVideos:
    @respx.mock
    async def test_returns_list_of_crawled_videos(self):
        respx.get("https://www.googleapis.com/youtube/v3/search").mock(
            return_value=Response(200, json=YOUTUBE_SEARCH_OK)
        )

        with patch("app.services.crawlers.youtube.settings") as mock_settings:
            mock_settings.youtube_api_key = "fake-key"
            videos = await crawler.fetch_latest_videos("UCxxxxxx")

        assert len(videos) == 2
        assert videos[0].platform_video_id == "vid001"
        assert videos[0].title == "Video One"
        assert videos[0].video_url == "https://www.youtube.com/watch?v=vid001"
        assert videos[0].thumbnail_url == "https://example.com/thumb1.jpg"

    @respx.mock
    async def test_published_at_is_parsed_from_iso_string(self):
        respx.get("https://www.googleapis.com/youtube/v3/search").mock(
            return_value=Response(200, json=YOUTUBE_SEARCH_OK)
        )

        with patch("app.services.crawlers.youtube.settings") as mock_settings:
            mock_settings.youtube_api_key = "fake-key"
            videos = await crawler.fetch_latest_videos("UCxxxxxx")

        assert videos[0].published_at.year == 2024
        assert videos[0].published_at.month == 1

    async def test_no_api_key_returns_empty_list(self):
        with patch("app.services.crawlers.youtube.settings") as mock_settings:
            mock_settings.youtube_api_key = ""
            videos = await crawler.fetch_latest_videos("UCxxxxxx")

        assert videos == []

    @respx.mock
    async def test_items_missing_video_id_are_skipped(self):
        respx.get("https://www.googleapis.com/youtube/v3/search").mock(
            return_value=Response(
                200, json={"items": [{"id": {}, "snippet": {"title": "no id"}}]}
            )
        )

        with patch("app.services.crawlers.youtube.settings") as mock_settings:
            mock_settings.youtube_api_key = "fake-key"
            videos = await crawler.fetch_latest_videos("UCxxxxxx")

        assert videos == []
