import re
from datetime import UTC, datetime
from urllib.parse import ParseResult, parse_qs, urlparse

import httpx

from app.core.config import get_settings
from app.models.models import Platform
from app.services.crawlers.base import BaseCrawler, CrawledVideo, CreatorInfo

settings = get_settings()


class YouTubeCrawler(BaseCrawler):
    platform = Platform.YOUTUBE

    async def resolve_creator(self, url: str) -> CreatorInfo:
        parsed = urlparse(url)
        if not settings.youtube_api_key:
            raise ValueError("YOUTUBE_API_KEY is required to resolve YouTube creators")
        channel_id = await self._extract_channel_id(parsed)
        if channel_id is None:
            raise ValueError("Unsupported YouTube creator URL")

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "snippet",
                    "id": channel_id,
                    "key": settings.youtube_api_key,
                },
            )
            response.raise_for_status()
            payload = response.json()

        items = payload.get("items") or []
        if not items:
            raise ValueError("Failed to resolve YouTube creator")
        snippet = items[0].get("snippet") or {}

        return CreatorInfo(
            platform_id=channel_id,
            name=snippet.get("title") or channel_id,
            profile_url=f"https://www.youtube.com/channel/{channel_id}",
            avatar_url=((snippet.get("thumbnails") or {}).get("high") or {}).get("url"),
            raw_data=items[0],
        )

    async def fetch_latest_videos(self, creator_id: str, limit: int = 20) -> list[CrawledVideo]:
        if not settings.youtube_api_key:
            return []

        # uploads playlist ID = replace leading "UC" with "UU"
        uploads_playlist_id = "UU" + creator_id[2:]
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/playlistItems",
                params={
                    "part": "snippet",
                    "playlistId": uploads_playlist_id,
                    "maxResults": min(limit, 50),
                    "key": settings.youtube_api_key,
                },
            )
            response.raise_for_status()
            payload = response.json()

        results: list[CrawledVideo] = []
        for item in payload.get("items") or []:
            snippet = item.get("snippet") or {}
            video_id = (snippet.get("resourceId") or {}).get("videoId")
            if not video_id:
                continue
            published_at = snippet.get("publishedAt")
            results.append(
                CrawledVideo(
                    platform_video_id=video_id,
                    title=snippet.get("title") or video_id,
                    video_url=f"https://www.youtube.com/watch?v={video_id}",
                    thumbnail_url=((snippet.get("thumbnails") or {}).get("high") or {}).get("url"),
                    published_at=datetime.fromisoformat((published_at or "").replace("Z", "+00:00"))
                    if published_at
                    else datetime.now(UTC),
                    raw_data=item,
                )
            )
        return results

    async def _extract_channel_id(self, parsed: ParseResult) -> str | None:
        url = parsed.geturl()
        channel_match = re.search(r"youtube\.com/channel/([\w-]+)", url)
        if channel_match:
            return channel_match.group(1)

        if "youtube.com" in url and "/@" in url:
            handle_match = re.search(r"youtube\.com/@([\w.-]+)", url)
            if handle_match:
                return await self._resolve_handle_to_channel_id(handle_match.group(1))

        query = parse_qs(parsed.query)
        if "channel_id" in query and query["channel_id"]:
            return query["channel_id"][0]

        return None

    async def _resolve_handle_to_channel_id(self, handle: str) -> str | None:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={
                    "part": "id",
                    "forHandle": handle,
                    "key": settings.youtube_api_key,
                },
            )
            response.raise_for_status()
            payload = response.json()

        items = payload.get("items") or []
        if not items:
            return None
        return items[0].get("id")
