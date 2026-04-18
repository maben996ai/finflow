import hashlib
import re
import time
from datetime import UTC, datetime
from functools import reduce
from urllib.parse import ParseResult, parse_qs, urlparse

import httpx

from app.core.config import get_settings

settings = get_settings()
from app.models.models import Platform
from app.services.crawlers.base import BaseCrawler, CrawledVideo, CreatorInfo

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/misc/sign/wbi.md
_MIXIN_KEY_ENC_TAB = [
    46, 47, 18,  2, 53,  8, 23, 32, 15, 50, 10, 31, 58,  3, 45, 35,
    27, 43,  5, 49, 33,  9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48,  7, 16, 24, 55, 40, 61, 26, 17,  0,  1, 60, 51, 30,  4,
    22, 25, 54, 21, 56, 59,  6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]


def _get_mixin_key(img_key: str, sub_key: str) -> str:
    s = img_key + sub_key
    return reduce(lambda acc, i: acc + s[i], _MIXIN_KEY_ENC_TAB, "")[:32]


def _wbi_sign(params: dict, mixin_key: str) -> dict:
    params = dict(params)
    params["wts"] = int(time.time())
    query = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    params["w_rid"] = hashlib.md5((query + mixin_key).encode()).hexdigest()
    return params


class BilibiliCrawler(BaseCrawler):
    platform = Platform.BILIBILI

    async def resolve_creator(self, url: str) -> CreatorInfo:
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=15) as client:
            parsed = await self._normalize_url(url, client)
            uid = await self._extract_uid(parsed, client)
            if uid is None:
                raise ValueError("Unsupported Bilibili creator URL")
            response = await client.get("https://api.bilibili.com/x/space/acc/info", params={"mid": uid})
            response.raise_for_status()
            payload = response.json()

        data = payload.get("data") or {}
        if payload.get("code") not in (0, None) or not data:
            raise ValueError("Failed to resolve Bilibili creator")

        return CreatorInfo(
            platform_id=str(data["mid"]),
            name=data.get("name") or f"Bilibili {uid}",
            profile_url=f"https://space.bilibili.com/{data['mid']}",
            avatar_url=data.get("face"),
            raw_data=data,
        )

    async def fetch_latest_videos(self, creator_id: str, limit: int = 20) -> list[CrawledVideo]:
        sessdata = settings.bilibili_sessdata
        if not sessdata:
            return []

        cookies = {"SESSDATA": sessdata}
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, cookies=cookies, timeout=20) as client:
            # Step 1: get buvid3/buvid4 for anti-bot
            spi = await client.get("https://api.bilibili.com/x/frontend/finger/spi")
            spi_data = spi.json().get("data", {})
            client.cookies.set("buvid3", spi_data.get("b_3", ""))
            client.cookies.set("buvid4", spi_data.get("b_4", ""))

            # Step 2: get WBI keys
            nav = await client.get("https://api.bilibili.com/x/web-interface/nav")
            wbi_img = nav.json()["data"]["wbi_img"]
            img_key = wbi_img["img_url"].split("/")[-1].split(".")[0]
            sub_key = wbi_img["sub_url"].split("/")[-1].split(".")[0]
            mixin_key = _get_mixin_key(img_key, sub_key)

            # Step 3: signed request to new endpoint
            params = _wbi_sign(
                {"mid": creator_id, "pn": 1, "ps": limit, "order": "pubdate"},
                mixin_key,
            )
            response = await client.get("https://api.bilibili.com/x/space/wbi/arc/search", params=params)
            response.raise_for_status()
            payload = response.json()

        data = payload.get("data") or {}
        videos = ((data.get("list") or {}).get("vlist")) or []
        results: list[CrawledVideo] = []
        for item in videos:
            bvid = item.get("bvid")
            if not bvid:
                continue
            results.append(
                CrawledVideo(
                    platform_video_id=bvid,
                    title=item.get("title") or bvid,
                    video_url=f"https://www.bilibili.com/video/{bvid}",
                    thumbnail_url=item.get("pic"),
                    published_at=datetime.fromtimestamp(item.get("created", 0), tz=UTC),
                    raw_data=item,
                )
            )
        return results

    async def _extract_uid(self, parsed: ParseResult, client: httpx.AsyncClient) -> str | None:
        url = parsed.geturl()
        space_match = re.search(r"space\.bilibili\.com/(\d+)", url)
        if space_match:
            return space_match.group(1)

        bv_match = re.search(r"/video/(BV[\w]+)", url)
        if bv_match:
            response = await client.get(
                "https://api.bilibili.com/x/web-interface/view",
                params={"bvid": bv_match.group(1)},
            )
            response.raise_for_status()
            payload = response.json()
            owner = (payload.get("data") or {}).get("owner") or {}
            mid = owner.get("mid")
            return str(mid) if mid else None

        query = parse_qs(parsed.query)
        if "mid" in query and query["mid"]:
            return query["mid"][0]

        return None

    async def _normalize_url(self, url: str, client: httpx.AsyncClient) -> ParseResult:
        parsed = urlparse(url)
        if parsed.netloc.lower().endswith("b23.tv"):
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return urlparse(str(response.url))
        return parsed
