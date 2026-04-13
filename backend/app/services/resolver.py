from dataclasses import dataclass
from urllib.parse import urlparse

from app.models.models import Platform


@dataclass
class ResolvedCreator:
    platform: Platform
    platform_creator_id: str
    name: str
    avatar_url: str | None = None


def resolve_creator(url: str) -> ResolvedCreator:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path_parts = [part for part in parsed.path.split("/") if part]
    slug = path_parts[-1] if path_parts else parsed.netloc

    if "bilibili" in host or host.endswith("b23.tv"):
        return ResolvedCreator(
            platform=Platform.BILIBILI,
            platform_creator_id=slug,
            name=f"Bilibili {slug}",
        )

    if "youtube.com" in host or "youtu.be" in host:
        return ResolvedCreator(
            platform=Platform.YOUTUBE,
            platform_creator_id=slug,
            name=f"YouTube {slug}",
        )

    raise ValueError("Unsupported creator URL")

